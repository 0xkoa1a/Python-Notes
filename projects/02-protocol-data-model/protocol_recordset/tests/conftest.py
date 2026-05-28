from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

# SRC is this exercise project's source directory.
# Adding it here lets pytest import protocol_recordset without packaging setup.
sys.path.insert(0, str(SRC))

