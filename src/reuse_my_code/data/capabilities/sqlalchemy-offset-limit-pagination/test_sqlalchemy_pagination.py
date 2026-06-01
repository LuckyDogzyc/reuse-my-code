from pathlib import Path


def test_helper_applies_offset_limit_and_count_query():
    source = Path("app/pagination/sqlalchemy_pagination.py").read_text(encoding="utf-8")
    assert ".offset(params.offset).limit(params.page_size)" in source
    assert "func.count" in source
    assert "statement.subquery()" in source
