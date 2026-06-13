"""Ensure the project root is on sys.path (loaded via runpy from Streamlit pages)."""
import sys
from pathlib import Path

_caller = globals().get("_streamlit_caller")
if not _caller:
    raise RuntimeError("_streamlit_caller missing; load this module via app._entry bootstrap")

caller = Path(_caller).resolve()
root = caller.parent.parent.parent if caller.parent.name == "pages" else caller.parent.parent
root_str = str(root)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
