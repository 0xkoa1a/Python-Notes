from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

# SRC is the local source directory for this exercise project.
# Adding it here lets pytest import mini_pipeline without installing a package.
sys.path.insert(0, str(SRC))

