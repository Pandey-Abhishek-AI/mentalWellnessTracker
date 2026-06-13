"""Ensure the project root is on sys.path for Streamlit entry points."""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
while _root != _root.parent and not (_root / "pyproject.toml").is_file():
    _root = _root.parent

_root_str = str(_root)
if _root_str not in sys.path:
    sys.path.insert(0, _root_str)
