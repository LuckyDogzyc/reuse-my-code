from pathlib import Path


def test_upload_route_template_orders_validation_before_storage():
    source = Path("app/api/upload_route.py").read_text(encoding="utf-8")
    assert source.index("validate_upload_file") < source.index("store_bytes")
    assert "require_role" in source
