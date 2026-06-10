"""pytest conftest — project 패키지를 sys.path에 추가."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
