from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile

from app.security.current_user import get_current_user
from app.security.permissions import require_role
from app.services.file_validation import validate_upload_file
from app.services.local_storage import store_bytes
from app.services.safe_filename import make_safe_filename

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("")
async def upload_file(
    file: UploadFile,
    current_user: dict = Depends(get_current_user),
) -> dict[str, str]:
    require_role("admin")(current_user)
    await validate_upload_file(file)
    safe_name = make_safe_filename(file.filename or "upload.bin")
    content = await file.read()
    stored_path = store_bytes(Path("uploads"), safe_name, content)
    return {"filename": safe_name, "path": str(stored_path)}
