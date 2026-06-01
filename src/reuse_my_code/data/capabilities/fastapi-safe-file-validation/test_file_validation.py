from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.services.file_validation import UploadValidationConfig, validate_upload_file


def make_file(name="a.png", content_type="image/png", data=b"abc"):
    return UploadFile(filename=name, file=BytesIO(data), headers={"content-type": content_type})


@pytest.mark.anyio
async def test_accepts_allowed_image_file():
    await validate_upload_file(make_file())


@pytest.mark.anyio
async def test_rejects_bad_extension():
    with pytest.raises(HTTPException) as exc:
        await validate_upload_file(make_file(name="shell.php"))
    assert exc.value.status_code == 400


@pytest.mark.anyio
async def test_rejects_oversized_file():
    config = UploadValidationConfig(max_file_size=2)
    with pytest.raises(HTTPException) as exc:
        await validate_upload_file(make_file(data=b"abc"), config)
    assert exc.value.status_code == 413
