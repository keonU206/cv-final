"""Refinement Dataset — (noisy, clean) image 쌍.

빠른 PoC를 위해 두 가지 모드 지원:
1. synthetic noise 모드 (기본): GT clean → 인공 noise(gaussian + jpeg) 추가하여 noisy 자동 생성
2. real SC-FEGAN output 모드: 사전 생성된 (input, output, target) 폴더 로드

발표 일정상 1번 모드로 학습 → 효과 검증 → 시간 남으면 2번.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Callable, Optional

import numpy as np

try:
    import cv2
    import torch
    from PIL import Image
    from torch.utils.data import Dataset
except ImportError as e:
    raise ImportError("torch, opencv-python, Pillow 필요") from e


def _to_neg1_1(img: np.ndarray) -> "torch.Tensor":
    """(H, W, 3) uint8 RGB → (3, H, W) float32 [-1, 1]."""
    arr = img.astype(np.float32) / 127.5 - 1.0
    return torch.from_numpy(arr).permute(2, 0, 1).contiguous()


def add_synthetic_noise(
    img: np.ndarray,
    gaussian_sigma: float = 8.0,
    jpeg_quality: int = 60,
    blur_p: float = 0.5,
    seed: Optional[int] = None,
) -> np.ndarray:
    """clean image에 SC-FEGAN-like artifact 인공 추가.

    조합:
    - Gaussian noise (학습 데이터 다양성)
    - JPEG compression (low-bitrate artifact 시뮬레이션)
    - 확률적 light blur (SC-FEGAN 경계 블러 유사)
    """
    rng = np.random.default_rng(seed)

    # 1. Gaussian noise
    noisy = img.astype(np.float32)
    noisy += rng.normal(0, gaussian_sigma, size=img.shape)
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)

    # 2. JPEG round-trip
    pil = Image.fromarray(noisy)
    buf = io.BytesIO()
    pil.save(buf, format="JPEG", quality=int(jpeg_quality))
    buf.seek(0)
    noisy = np.array(Image.open(buf))

    # 3. 선택적 light blur
    if rng.random() < blur_p:
        k = int(rng.choice([3, 5]))
        noisy = cv2.GaussianBlur(noisy, (k, k), 0)

    return noisy


class SyntheticRefinementDataset(Dataset):
    """clean image 폴더에서 synthetic noisy 쌍 생성.

    Args:
        image_dir: clean image .jpg/.png 폴더.
        size: 출력 크기 (기본 512).
        gaussian_sigma: noise σ.
        jpeg_quality: 1~100 (낮을수록 강한 artifact).
        subset_size: 사용할 이미지 개수 제한 (None=전체).
        seed: noise 재현성.
    """

    EXTS = (".jpg", ".jpeg", ".png", ".webp")

    def __init__(
        self,
        image_dir: str | Path,
        size: int = 512,
        gaussian_sigma: float = 8.0,
        jpeg_quality: int = 60,
        subset_size: Optional[int] = None,
        seed: int = 0,
    ) -> None:
        self.image_dir = Path(image_dir)
        if not self.image_dir.exists():
            raise FileNotFoundError(self.image_dir)
        self.size = size
        self.gaussian_sigma = gaussian_sigma
        self.jpeg_quality = jpeg_quality
        self.seed = seed

        paths = sorted(
            p for p in self.image_dir.rglob("*") if p.suffix.lower() in self.EXTS
        )
        if not paths:
            raise FileNotFoundError(f"no images in {self.image_dir}")
        if subset_size is not None:
            paths = paths[: int(subset_size)]
        self.paths = paths

    def __len__(self) -> int:
        return len(self.paths)

    def _load(self, path: Path) -> np.ndarray:
        img = cv2.imread(str(path))
        if img is None:
            raise IOError(f"failed to read {path}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if img.shape[:2] != (self.size, self.size):
            img = cv2.resize(img, (self.size, self.size))
        return img

    def __getitem__(self, idx: int) -> dict:
        clean = self._load(self.paths[idx])
        noisy = add_synthetic_noise(
            clean,
            gaussian_sigma=self.gaussian_sigma,
            jpeg_quality=self.jpeg_quality,
            seed=self.seed + idx,  # 샘플별 재현성
        )
        return {
            "input": _to_neg1_1(noisy),    # (3, H, W) [-1, 1]
            "target": _to_neg1_1(clean),
        }


class PairedRefinementDataset(Dataset):
    """사전 생성된 (input, target) 쌍 폴더 로드 (real SC-FEGAN output).

    구조:
        root/
            inputs/  *.png  (SC-FEGAN output)
            targets/ *.png  (GT clean)
        파일명 일치로 매칭.
    """

    EXTS = (".jpg", ".jpeg", ".png", ".webp")

    def __init__(self, root: str | Path, size: int = 512) -> None:
        self.root = Path(root)
        in_dir = self.root / "inputs"
        tg_dir = self.root / "targets"
        if not in_dir.exists() or not tg_dir.exists():
            raise FileNotFoundError(f"{in_dir} / {tg_dir}")
        self.size = size

        in_paths = sorted(
            p for p in in_dir.iterdir() if p.suffix.lower() in self.EXTS
        )
        self.pairs = []
        for ip in in_paths:
            tp = tg_dir / ip.name
            if tp.exists():
                self.pairs.append((ip, tp))
        if not self.pairs:
            raise FileNotFoundError("no matched pairs")

    def __len__(self) -> int:
        return len(self.pairs)

    def _load(self, path: Path) -> np.ndarray:
        img = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
        if img.shape[:2] != (self.size, self.size):
            img = cv2.resize(img, (self.size, self.size))
        return img

    def __getitem__(self, idx: int) -> dict:
        ip, tp = self.pairs[idx]
        return {
            "input": _to_neg1_1(self._load(ip)),
            "target": _to_neg1_1(self._load(tp)),
        }
