"""SC-FEGAN 9채널 입력 자동 생성 모듈.

- mask.py:     시술 영역 binary mask (procedure dict 기반)
- color.py:    시술 영역 색상 가이드 (procedure dict 기반)
- sketch.py:   시술별 가이드 라인 sketch (procedure_id 문자열 기반)
- composer.py: 9채널 입력 통합 (sketch + color + mask + noise + incomplete)
"""
from .color import make_color, make_color_simple
from .composer import (
    PROCEDURE_ID_TO_SKETCH,
    compose_and_pack,
    compose_scfegan_input,
    load_procedures,
    to_scfegan_tensor,
)
from .mask import make_mask
from .sketch import (
    SKETCH_GENERATORS,
    generate_double_eyelid_sketch,
    generate_nose_tip_sketch,
    generate_sketch,
    generate_v_line_sketch,
)

__all__ = [
    # mask
    "make_mask",
    # color
    "make_color",
    "make_color_simple",
    # sketch
    "generate_sketch",
    "generate_nose_tip_sketch",
    "generate_double_eyelid_sketch",
    "generate_v_line_sketch",
    "SKETCH_GENERATORS",
    # composer
    "compose_scfegan_input",
    "to_scfegan_tensor",
    "compose_and_pack",
    "load_procedures",
    "PROCEDURE_ID_TO_SKETCH",
]
