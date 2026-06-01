from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile, status


@dataclass(frozen=True)
class UploadValidationConfig:
    max_file_size: int = 5 * 1024 * 1024
    allowed_extensions: frozenset[str] = frozenset({".jpg", ".jpeg", ".png", ".webp"})
    allowed_content_types: frozenset[str] = frozenset({"image/jpeg", "image/png", "image/webp"})


async def validate_upload_file(
    file: UploadFile,
    config: UploadValidationConfig = UploadValidationConfig(),
) -> None:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if not filename.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing filename")
    if suffix not in config.allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported file extension")
    if file.content_type not in config.allowed_content_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported content type")

    position = await file.seek(0)
    content = await file.read(config.max_file_size + 1)
    await file.seek(position or 0)
    if len(content) > config.max_file_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="file too large")
