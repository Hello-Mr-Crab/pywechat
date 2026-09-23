"""pytest bootstrap: ensure the repo root is importable so that the
`contact_exporter` package resolves regardless of invocation directory.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
