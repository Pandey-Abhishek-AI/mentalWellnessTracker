"""Shared bootstrap for all Streamlit entry files."""

import runpy
from pathlib import Path


def ensure_project_path(caller_file: str) -> None:
    caller = Path(caller_file).resolve()
    entry = caller.parent / "_entry.py"
    if not entry.is_file():
        entry = caller.parent.parent / "_entry.py"
    runpy.run_path(str(entry), init_globals={"_streamlit_caller": str(caller)})


_caller = globals().get("_streamlit_caller")
if _caller:
    ensure_project_path(_caller)
