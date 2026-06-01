from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

_SAFE_CHARS = re.compile(r"[^a-zA-Z0-9._-]+")


def make_safe_filename(original_filename: str) -> str:
    suffix = Path(original_filename or "").suffix.lower()
    stem = Path(original_filename or "file").stem
    stem = _SAFE_CHARS.sub("-", stem).strip(".-_") or "file"
    return f"{stem[:64]}-{uuid4().hex}{suffix}"
