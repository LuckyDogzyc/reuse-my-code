from __future__ import annotations

from pathlib import Path


class UnsafeStoragePath(ValueError):
    pass


def store_bytes(base_dir: Path, filename: str, data: bytes) -> Path:
    base_dir = base_dir.resolve()
    target = (base_dir / filename).resolve()
    if base_dir not in target.parents and target != base_dir:
        raise UnsafeStoragePath("target path escapes base directory")
    base_dir.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target
