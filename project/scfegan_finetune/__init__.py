"""SC-FEGAN Fine-tuning (Phase 7-C1).

CelebAMask-HQ 2,000장으로 G+D 추가 학습 → 한국인 얼굴 도메인 적응.

⚠ TF 1.x 환경 필요:
    os.environ['TF_USE_LEGACY_KERAS'] = '1'
    import tensorflow.compat.v1 as tf
    tf.disable_v2_behavior()

모듈:
- data_pipeline.py: 학습 데이터 sampling + 9채널 입력 생성
- train_finetune.py: TF 1.x 학습 루프 스켈레톤
"""
from .data_pipeline import (
    FineTuneSamplePack,
    build_finetune_sample,
    iter_finetune_samples,
    sample_celebamask_subset,
)

__all__ = [
    "sample_celebamask_subset",
    "build_finetune_sample",
    "iter_finetune_samples",
    "FineTuneSamplePack",
]
