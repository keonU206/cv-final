"""시술별 자동 색상 가이드 생성 — SC-FEGAN의 color channel 입력.

mask 영역 안에 자연스러운 색을 채워 SC-FEGAN에 "이 영역을 이런 색으로
복원해라" 가이드 제공. 색은 원본 이미지에서 시술 영역 주변의 피부톤을
sample하여 사용하며, 시술 종류에 따라 HSV V값을 ±조정하여 하이라이트/음영
효과를 추가한다.

전체 흐름:
1. mask 영역 계산 (make_mask 재사용 가능)
2. mask 바깥 ring에서 피부톤 median sample
3. 시술별 HSV 조정 (nose=하이라이트, eye=음영, jaw=피부톤 그대로)
4. mask 안을 sample 색으로 채움 + Gaussian blur로 자연스러운 그라데이션
5. (size, size, 3) uint8 출력 (RGB)
"""
from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from .mask import make_mask

# 시술 영역(region)별 기본 HSV V 조정값 — 시술 특성에 맞는 색감 차이
# nose_tip: 코끝 하이라이트 (V+12 → 약간 밝게)
# double_eyelid: 쌍커풀 음영 라인 (V-18 → 약간 어둡게)
# jaw_v_line: 턱선 (V+0 → 피부톤 그대로)
DEFAULT_V_OFFSET = {
    "nose": 12,
    "eye": -18,
    "jaw": 0,
    "mouth": -5,
}


def _sample_skin_tone(
    image: np.ndarray, mask: np.ndarray, ring_px: int = 8
) -> np.ndarray:
    """mask 바깥 ring에서 피부톤 median 색 추출.

    Args:
        image: (H, W, 3) uint8 RGB.
        mask: (H, W) 또는 (H, W, 1) uint8 binary (255=영역).
        ring_px: ring 두께 (px).

    Returns:
        (3,) uint8 RGB — 추출된 피부톤 (실패 시 default 살색).
    """
    if mask.ndim == 3:
        mask = mask[..., 0]

    kernel = np.ones((ring_px, ring_px), np.uint8)
    dilated = cv2.dilate(mask, kernel)
    outer_ring = cv2.subtract(dilated, mask)

    ys, xs = np.where(outer_ring > 0)
    if len(ys) == 0:
        # mask가 이미지 가장자리에 붙어있거나 ring이 비어있는 경우
        return np.array([210, 180, 160], dtype=np.uint8)

    pixels = image[ys, xs]  # (N, 3)
    return np.median(pixels, axis=0).astype(np.uint8)


def _adjust_hsv_v(color_rgb: np.ndarray, v_offset: int) -> np.ndarray:
    """RGB 색의 HSV V값을 ±조정 후 RGB로 복귀.

    Args:
        color_rgb: (3,) uint8 RGB.
        v_offset: V 채널 가감값 (-255 ~ +255).

    Returns:
        (3,) uint8 RGB — V 조정된 색.
    """
    if v_offset == 0:
        return color_rgb.copy()

    bgr_pixel = color_rgb[::-1].reshape(1, 1, 3).astype(np.uint8)
    hsv = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV).astype(np.int16)
    hsv[0, 0, 2] = np.clip(hsv[0, 0, 2] + v_offset, 0, 255)
    bgr_out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return bgr_out[0, 0, ::-1].copy()


def make_color(
    image: np.ndarray,
    landmarks: np.ndarray,
    procedure: dict[str, Any],
    size: int = 512,
    blur_sigma: float = 11.0,
) -> np.ndarray:
    """시술 정의에 따라 (size, size, 3) RGB 색상 가이드 생성.

    Args:
        image: (size, size, 3) uint8 RGB. 원본 이미지 (피부톤 sampling용).
        landmarks: (478, 2) int32 정규화 공간 좌표.
        procedure: procedures.yaml의 한 항목.
            추가 가능 필드:
            - color_v_offset: int — region 기본값을 override할 V 조정값.
            - color_blur_sigma: float — Gaussian blur σ override.
        size: 출력 크기.
        blur_sigma: Gaussian blur σ — 영역 경계 부드럽게.

    Returns:
        (size, size, 3) uint8 RGB. mask 안은 sample 색, 밖은 0.

    Raises:
        ValueError: image 크기가 size와 다르거나 mask가 비어있을 때.
    """
    if image.shape[:2] != (size, size):
        raise ValueError(
            f"image shape {image.shape[:2]} != ({size}, {size}). "
            f"호출 전 resize 필요."
        )

    mask = make_mask(landmarks, procedure, size=size)  # (size, size, 1)
    mask_2d = mask[..., 0]

    if mask_2d.sum() == 0:
        raise ValueError(
            f"procedure={procedure.get('id')!r}의 mask가 비어있음 "
            f"(랜드마크 좌표 검증 필요)."
        )

    # 피부톤 sample (mask 바깥 ring)
    skin_rgb = _sample_skin_tone(image, mask_2d)

    # 시술 region별 V offset 결정 (procedure override 우선)
    region = procedure.get("region", "")
    v_offset = procedure.get("color_v_offset", DEFAULT_V_OFFSET.get(region, 0))
    final_rgb = _adjust_hsv_v(skin_rgb, int(v_offset))

    # mask 영역을 final_rgb로 채움
    color_canvas = np.zeros((size, size, 3), dtype=np.uint8)
    color_canvas[mask_2d > 0] = final_rgb

    # Gaussian blur로 경계 자연스럽게
    sigma = float(procedure.get("color_blur_sigma", blur_sigma))
    if sigma > 0:
        ksize = max(3, int(sigma * 4) | 1)  # 홀수 보장
        color_canvas = cv2.GaussianBlur(
            color_canvas, (ksize, ksize), sigmaX=sigma, sigmaY=sigma
        )

    # blur 후 mask 밖은 다시 0으로 강제 (영역 침범 방지)
    soft_mask = cv2.GaussianBlur(
        mask_2d.astype(np.float32) / 255.0,
        (max(3, int(sigma * 2) | 1), max(3, int(sigma * 2) | 1)),
        sigmaX=sigma, sigmaY=sigma,
    )[..., None]
    color_canvas = (color_canvas.astype(np.float32) * soft_mask).astype(np.uint8)

    return color_canvas


def make_color_simple(
    landmarks: np.ndarray,
    procedure: dict[str, Any],
    size: int = 512,
    fallback_rgb: tuple[int, int, int] = (210, 180, 160),
) -> np.ndarray:
    """원본 이미지 없이 fallback 색만으로 색상 가이드 생성 (테스트용).

    Args:
        landmarks: (478, 2) int32.
        procedure: procedures.yaml 항목.
        size: 출력 크기.
        fallback_rgb: image 없이 사용할 기본 살색.

    Returns:
        (size, size, 3) uint8 RGB.
    """
    fake_image = np.full((size, size, 3), fallback_rgb, dtype=np.uint8)
    return make_color(fake_image, landmarks, procedure, size=size)
