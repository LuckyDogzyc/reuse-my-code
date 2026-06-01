from fastapi import HTTPException

from app.pagination.params import PaginationParams


def test_calculates_offset():
    assert PaginationParams(page=3, page_size=20).offset == 40


def test_rejects_invalid_page():
    try:
        PaginationParams(page=0)
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("expected HTTPException")


def test_caps_page_size():
    assert PaginationParams(page_size=500, max_page_size=100).page_size == 100
