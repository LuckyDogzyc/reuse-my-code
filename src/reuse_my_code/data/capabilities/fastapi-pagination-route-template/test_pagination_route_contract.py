from pathlib import Path


def test_pagination_route_uses_helpers():
    source = Path("app/api/pagination_route.py").read_text(encoding="utf-8")
    assert "PaginationParams" in source
    assert "paginate_select" in source
    assert "PaginatedResponse" in source
