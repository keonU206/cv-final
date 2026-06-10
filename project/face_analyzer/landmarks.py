"""MediaPipe Face Landmarker (Tasks API) 래퍼.

478개 랜드마크(468 face + 10 iris)를 검출한다.
- Tasks API 사용 (legacy mp.solutions.face_mesh는 protobuf 충돌 회피)
- 첫 호출 시 모델(.task) 파일을 /tmp 에 자동 다운로드
"""
from __future__ import annotations

import os
import urllib.request

import numpy as np

try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
except ImportError as e:
    raise ImportError(
        "mediapipe가 필요합니다. `pip install mediapipe` 를 실행하세요."
    ) from e


class LandmarkDetectionError(RuntimeError):
    """얼굴 검출 실패 시 발생."""


_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)
_MODEL_PATH = "/tmp/face_landmarker.task"
_DETECTOR = None


def _ensure_model() -> str:
    if not os.path.exists(_MODEL_PATH):
        print(f"Downloading face_landmarker.task → {_MODEL_PATH}")
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
    return _MODEL_PATH


def _get_detector():
    global _DETECTOR
    if _DETECTOR is None:
        model_path = _ensure_model()
        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            running_mode=mp_vision.RunningMode.IMAGE,
        )
        _DETECTOR = mp_vision.FaceLandmarker.create_from_options(options)
    return _DETECTOR


def detect_landmarks(image: np.ndarray) -> np.ndarray:
    """BGR 이미지에서 478개 랜드마크 픽셀 좌표를 검출한다.

    Args:
        image: (H, W, 3) BGR uint8 ndarray.

    Returns:
        (478, 2) int32 ndarray. 각 행은 (x, y) 픽셀 좌표.

    Raises:
        LandmarkDetectionError: 얼굴을 찾지 못한 경우.
    """
    if image is None or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(
            f"3채널 BGR 이미지가 필요합니다. got shape="
            f"{None if image is None else image.shape}"
        )

    h, w = image.shape[:2]
    rgb = np.ascontiguousarray(image[..., ::-1])
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    detector = _get_detector()
    result = detector.detect(mp_image)

    if not result.face_landmarks:
        raise LandmarkDetectionError("얼굴을 찾지 못했습니다.")

    landmarks = result.face_landmarks[0]
    pts = np.array(
        [(int(lm.x * w), int(lm.y * h)) for lm in landmarks],
        dtype=np.int32,
    )
    return pts
