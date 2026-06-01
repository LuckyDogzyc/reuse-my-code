import pytest

from app.services.local_storage import UnsafeStoragePath, store_bytes


def test_writes_bytes(tmp_path):
    target = store_bytes(tmp_path, "a.txt", b"hello")
    assert target.read_bytes() == b"hello"


def test_rejects_path_escape(tmp_path):
    with pytest.raises(UnsafeStoragePath):
        store_bytes(tmp_path, "../escape.txt", b"bad")
