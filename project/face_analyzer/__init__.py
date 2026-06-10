"""face_analyzer 패키지.

ratios는 numpy만 필요해 즉시 import.
landmarks/normalize는 mediapipe/opencv 의존이라 lazy import.
"""
from .ratios import compute_ratios

__all__ = [
    "compute_ratios",
    "detect_landmarks",
    "LandmarkDetectionError",
    "normalize_face",
    "NormalizeMeta",
]


def __getattr__(name: str):
    if name in ("detect_landmarks", "LandmarkDetectionError"):
        from . import landmarks
        return getattr(landmarks, name)
    if name in ("normalize_face", "NormalizeMeta"):
        from . import normalize
        return getattr(normalize, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
