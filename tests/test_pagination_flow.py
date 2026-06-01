from reuse_my_code.models import BundleRequest, PlanRequest, SearchRequest
from reuse_my_code.planner import plan_tasks
from reuse_my_code.registry import build_bundle, get_capability, search_capabilities


def test_fastapi_pagination_goal_is_decomposed_into_task_level_capabilities():
    plan = plan_tasks(PlanRequest(goal="给我的 FastAPI 项目加一个分页查询接口", language="python", framework="fastapi"))

    capabilities = [task.capability for task in plan.tasks]
    assert capabilities[:4] == [
        "pagination_params",
        "sqlalchemy_pagination",
        "paginated_response_schema",
        "fastapi_pagination_route",
    ]
    assert "customer_project_integration_test" in capabilities


def test_search_returns_pagination_params_capability():
    result = search_capabilities(SearchRequest(capability="pagination_params", language="python", framework="fastapi"))

    assert result.matches
    assert result.matches[0].asset_id == "fastapi-pagination-params"


def test_get_pagination_capability_returns_code_tests_and_instructions():
    detail = get_capability("fastapi-pagination-params")

    assert detail is not None
    assert {file.role for file in detail.files} == {"core", "unit_test"}
    assert detail.unit_test is not None
    assert detail.instructions_for_agent


def test_pagination_bundle_matches_platform_provided_tasks():
    bundle = build_bundle(BundleRequest(goal="给我的 FastAPI 项目加一个分页查询接口", language="python", framework="fastapi"))

    matched_assets = [result.selected.asset_id for result in bundle.results if result.selected]
    assert "fastapi-pagination-params" in matched_assets
    assert "sqlalchemy-offset-limit-pagination" in matched_assets
    assert "fastapi-paginated-response-schema" in matched_assets
    assert "fastapi-pagination-route-template" in matched_assets
