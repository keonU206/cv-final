"""CelebAMask-HQ Hybrid Dataset.

이미지와 마스크가 다른 데이터셋에서 옴:
- 이미지: `mattymchen/celeba-hq` (1024×1024 JPG, 인덱스 0~29999)
- 마스크: `limsanky/celebamask-hq-256` 의 `mask-anno-256/{N}` 행

페어링: mattymchen 인덱스 N = mask-anno-256/{N}.

옵션: use_landmark=True 시 MediaPipe 478점에서 Gaussian heatmap을
4번째 채널로 추가 → LM-guided U-Net 입력 (4채널).
"""
from __future__ import annotations

import os
import pickle
import random
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import cv2
    import torch
    from torch.utils.data import Dataset
except ImportError as e:
    raise ImportError("PyTorch + OpenCV가 필요합니다.") from e

try:
    from datasets import load_dataset
except ImportError as e:
    raise ImportError("`pip install datasets`") from e

from .label_map import remap
from .heatmap import landmark_heatmap


class CelebAMaskHQDataset(Dataset):
    """Hybrid: mattymchen 이미지 + limsanky 마스크.

    각 sample: (image_tensor, mask_tensor_long)
      - image: (C, 256, 256) float, ImageNet 정규화
              C=3 (use_landmark=False) 또는 C=4 (use_landmark=True)
      - mask:  (256, 256) long, 클래스 0~5
    """

    IMAGE_DATASET = "mattymchen/celeba-hq"
    MASK_DATASET = "limsanky/celebamask-hq-256"
    SPLIT_SEED = 42
    SPLIT_RATIOS = {"train": (0.0, 0.8), "val": (0.8, 0.9), "test": (0.9, 1.0)}

    def __init__(
        self,
        split: str = "train",
        transform=None,
        subset_size: Optional[int] = None,
        cache_dir: str = "/content/cv-final-cache",
        verbose: bool = True,
        input_size: int = 256,
        use_landmark: bool = False,
        landmark_sigma: float = 3.0,
    ):
        if split not in self.SPLIT_RATIOS:
            raise ValueError(f"split must be train/val/test, got {split!r}")

        self.transform = transform
        self.verbose = verbose
        self.input_size = input_size
        self.use_landmark = use_landmark
        self.landmark_sigma = landmark_sigma
        self.cache_dir = Path(cache_dir)

        # 1) 이미지 데이터셋 로드 (mattymchen)
        if verbose:
            print(f"[Dataset] loading images: {self.IMAGE_DATASET}")
        self.ds_images = load_dataset(self.IMAGE_DATASET, split="train")
        if verbose:
            print(f"[Dataset]   → {len(self.ds_images)} images")

        # 2) 마스크 데이터셋 로드 (limsanky)
        if verbose:
            print(f"[Dataset] loading masks: {self.MASK_DATASET}")
        self.ds_masks = load_dataset(self.MASK_DATASET, split="train")
        if verbose:
            print(f"[Dataset]   → {len(self.ds_masks)} rows")

        # 3) 마스크 인덱스 빌드: {N: mask_dataset_idx} (캐싱)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        mask_cache = self.cache_dir / "mask_index.pkl"
        if mask_cache.exists():
            with open(mask_cache, "rb") as f:
                self.mask_index = pickle.load(f)
            if verbose:
                print(f"[Dataset] mask index cache hit: {len(self.mask_index)} entries")
        else:
            if verbose:
                print("[Dataset] building mask index... (~1-2분)")
            self.mask_index = self._build_mask_index()
            with open(mask_cache, "wb") as f:
                pickle.dump(self.mask_index, f)
            if verbose:
                print(f"[Dataset]   → {len(self.mask_index)} mask entries cached")

        # 4) Pair 생성 + split
        self.pairs = self._build_split_pairs(split)
        if verbose:
            print(f"[Dataset] split={split}: {len(self.pairs)} pairs")

        # 5) Subset
        if subset_size is not None and subset_size < len(self.pairs):
            self.pairs = self.pairs[:subset_size]
            if verbose:
                print(f"[Dataset] subset: 처음 {subset_size}개만 사용")

        # 6) Landmark cache (선택)
        self.landmark_cache: Optional[dict[int, np.ndarray]] = None
        if self.use_landmark:
            self._load_or_build_landmark_cache()

    # ─── 마스크 인덱스 빌드 (한 번만) ───
    def _build_mask_index(self) -> dict[int, int]:
        idx_map: dict[int, int] = {}
        for idx in range(len(self.ds_masks)):
            key = self.ds_masks[idx]["__key__"]
            parts = key.split("/")
            if len(parts) < 2:
                continue
            folder, fname = parts[-2], parts[-1]
            if folder != "mask-anno-256":
                continue
            try:
                n = int(fname)
            except ValueError:
                continue
            idx_map[n] = idx
        return idx_map

    # ─── Split + 페어링 ───
    def _build_split_pairs(self, split: str) -> list[tuple[int, int]]:
        n_images = len(self.ds_images)
        common_ids = sorted(n for n in self.mask_index if n < n_images)

        rng = random.Random(self.SPLIT_SEED)
        shuffled = list(common_ids)
        rng.shuffle(shuffled)

        start_r, end_r = self.SPLIT_RATIOS[split]
        n_total = len(shuffled)
        ids = shuffled[int(n_total * start_r) : int(n_total * end_r)]

        return [(n, self.mask_index[n]) for n in ids]

    # ─── Landmark cache ───
    def _load_or_build_landmark_cache(self):
        """MediaPipe 랜드마크 캐시 — 24K 이미지 × 478점.

        첫 실행: 10~15분 (MediaPipe로 추출).
        이후: pickle 즉시 로드.
        """
        cache_path = self.cache_dir / "landmarks.pkl"
        if cache_path.exists():
            with open(cache_path, "rb") as f:
                self.landmark_cache = pickle.load(f)
            if self.verbose:
                print(
                    f"[Dataset] landmark cache hit: "
                    f"{len(self.landmark_cache)} entries"
                )
            return

        # 캐시 빌드
        if self.verbose:
            print("[Dataset] building landmark cache... (10~15분, 1회만)")

        # MediaPipe lazy import (heavy dep)
        try:
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision as mp_vision
            import mediapipe as mp
        except ImportError as e:
            raise ImportError(
                "mediapipe가 필요합니다. `pip install mediapipe==0.10.21`"
            ) from e

        # face_landmarker.task 다운로드
        import urllib.request
        model_path = "/tmp/face_landmarker.task"
        if not os.path.exists(model_path):
            url = (
                "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
                "face_landmarker/float16/1/face_landmarker.task"
            )
            urllib.request.urlretrieve(url, model_path)

        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            running_mode=mp_vision.RunningMode.IMAGE,
        )
        detector = mp_vision.FaceLandmarker.create_from_options(options)

        # 모든 페어에 대해 랜드마크 추출
        cache: dict[int, np.ndarray] = {}
        skipped = 0

        try:
            from tqdm.auto import tqdm
            iterable = tqdm(self.pairs, desc="landmark extraction")
        except ImportError:
            iterable = self.pairs

        for image_idx, _ in iterable:
            img_pil = self.ds_images[image_idx]["image"]
            img_rgb = np.array(img_pil.convert("RGB"))
            # 256으로 리사이즈 (heatmap 좌표 일치)
            img_256 = cv2.resize(
                img_rgb, (self.input_size, self.input_size),
                interpolation=cv2.INTER_AREA,
            )
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_256)
            result = detector.detect(mp_image)

            if not result.face_landmarks:
                skipped += 1
                continue

            lms = result.face_landmarks[0]
            pts = np.array(
                [(lm.x * self.input_size, lm.y * self.input_size) for lm in lms],
                dtype=np.float32,
            )
            cache[image_idx] = pts

        if self.verbose:
            print(
                f"[Dataset]   → {len(cache)} landmarks (skipped {skipped})"
            )

        with open(cache_path, "wb") as f:
            pickle.dump(cache, f)
        self.landmark_cache = cache

    # ─── PyTorch Dataset API ───
    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx: int):
        image_idx, mask_idx = self.pairs[idx]

        # 원본 얼굴 (mattymchen, 1024×1024 JPG)
        img_pil = self.ds_images[image_idx]["image"]
        image = np.array(img_pil.convert("RGB"))  # (H, W, 3) uint8

        # 256으로 리사이즈
        if image.shape[0] != self.input_size or image.shape[1] != self.input_size:
            image = cv2.resize(
                image, (self.input_size, self.input_size),
                interpolation=cv2.INTER_AREA,
            )

        # 마스크
        mask_pil = self.ds_masks[mask_idx]["png"]
        mask_19 = np.array(mask_pil)
        if mask_19.ndim == 3:
            mask_19 = mask_19[..., 0]
        mask_6 = remap(mask_19)

        # Landmark heatmap (선택)
        heatmap = None
        if self.use_landmark and self.landmark_cache is not None:
            if image_idx in self.landmark_cache:
                lm = self.landmark_cache[image_idx]
                heatmap = landmark_heatmap(
                    lm.astype(np.int32),
                    size=self.input_size,
                    sigma=self.landmark_sigma,
                )  # (H, W) float32 [0, 1]
            else:
                # 캐시에 없음 → 0 heatmap
                heatmap = np.zeros(
                    (self.input_size, self.input_size), dtype=np.float32
                )

        # Transform 적용
        if self.transform is not None:
            if heatmap is not None:
                # additional_targets로 heatmap 같이 변환
                t = self.transform(image=image, mask=mask_6, heatmap=heatmap)
                image = t["image"]
                mask_6 = t["mask"]
                heatmap = t["heatmap"]
            else:
                t = self.transform(image=image, mask=mask_6)
                image = t["image"]
                mask_6 = t["mask"]
        else:
            image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
            mask_6 = torch.from_numpy(mask_6)

        # Heatmap을 채널 추가
        if heatmap is not None:
            # image: torch (3, H, W) → (4, H, W)
            if isinstance(heatmap, np.ndarray):
                heatmap_t = torch.from_numpy(heatmap).float().unsqueeze(0)
            else:
                # ToTensorV2 이미 적용된 경우
                heatmap_t = heatmap.float()
                if heatmap_t.ndim == 2:
                    heatmap_t = heatmap_t.unsqueeze(0)
            image = torch.cat([image, heatmap_t], dim=0)

        if isinstance(mask_6, np.ndarray):
            mask_6 = torch.from_numpy(mask_6)
        return image, mask_6.long()
