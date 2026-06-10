"""Refinement Network — SC-FEGAN 출력 정제 (Phase 7-B).

모듈:
- model.py:   작은 U-Net + residual wrapper
- losses.py:  L1 + Perceptual (VGG19)
- data.py:    Synthetic / Paired Dataset
- train.py:   학습 진입점
"""
from .data import (
    PairedRefinementDataset,
    SyntheticRefinementDataset,
    add_synthetic_noise,
)
from .losses import RefinementLoss, VGGPerceptual
from .model import (
    RefinementWrapper,
    build_refinement_net,
    build_refinement_wrapper,
)

__all__ = [
    "build_refinement_net",
    "build_refinement_wrapper",
    "RefinementWrapper",
    "VGGPerceptual",
    "RefinementLoss",
    "SyntheticRefinementDataset",
    "PairedRefinementDataset",
    "add_synthetic_noise",
]
