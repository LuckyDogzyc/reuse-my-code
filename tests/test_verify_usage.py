from pathlib import Path

from reuse_my_code.models import VerifyRequest
from reuse_my_code.registry import get_capability, verify_usage


def write_capability_files(project_root: Path, asset_id: str) -> None:
    detail = get_capability(asset_id)
    assert detail is not None
    for file in detail.files:
        target = project_root / file.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(file.content, encoding="utf-8")


def test_verify_usage_reports_missing_files(tmp_path):
    result = verify_usage(
        VerifyRequest(asset_id="fastapi-safe-file-validation", project_path=str(tmp_path))
    )

    assert result.status == "missing"
    assert result.files
    assert any(not file.exists for file in result.files)


def test_verify_usage_reports_verified_when_files_match(tmp_path):
    write_capability_files(tmp_path, "fastapi-safe-file-validation")

    result = verify_usage(
        VerifyRequest(asset_id="fastapi-safe-file-validation", project_path=str(tmp_path))
    )

    assert result.status == "verified"
    assert result.unit_test_command == "pytest tests/test_file_validation.py"
    assert all(file.hash_match for file in result.files)


def test_verify_usage_reports_modified_when_hash_differs(tmp_path):
    write_capability_files(tmp_path, "fastapi-safe-file-validation")
    target = tmp_path / "app/services/file_validation.py"
    target.write_text(target.read_text(encoding="utf-8") + "\n# local modification\n", encoding="utf-8")

    result = verify_usage(
        VerifyRequest(asset_id="fastapi-safe-file-validation", project_path=str(tmp_path))
    )

    assert result.status == "modified"
    assert any(file.exists and not file.hash_match for file in result.files)


def test_verify_usage_reports_not_found_for_unknown_asset(tmp_path):
    result = verify_usage(VerifyRequest(asset_id="missing", project_path=str(tmp_path)))

    assert result.status == "not_found"
