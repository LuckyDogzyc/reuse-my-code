from app.pagination.response import PaginatedResponse


def test_computes_total_pages():
    response = PaginatedResponse.create(items=[1, 2], total=41, page=1, page_size=20)
    assert response.total_pages == 3
    assert response.items == [1, 2]
