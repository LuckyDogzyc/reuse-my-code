from fastapi.testclient import TestClient

from reuse_my_code.api import app
from reuse_my_code.models import BundleRequest, PlanRequest, SearchRequest
from reuse_my_code.planner import plan_tasks
from reuse_my_code.registry import build_bundle, get_capability, search_capabilities


def test_safe_upload_goal_is_decomposed_into_medium_grained_tasks():
    plan = plan_tasks(
        PlanRequest(goal="给我的 FastAPI 项目加一个安全文件上传功能", language="python", framework="fastapi")
    )

    capabilities = [task.capability for task in plan.tasks]
    assert "safe_file_validation" in capabilities
    assert "safe_filename_generation" in capabilities
    assert "local_file_storage" in capabilities
    assert "customer_project_integration_test" in capabilities


def test_search_returns_task_level_capability():
    result = search_capabilities(
        SearchRequest(capability="safe_file_validation", language="python", framework="fastapi")
    )

    assert result.matches
    assert result.matches[0].asset_id == "fastapi-safe-file-validation"
    assert result.matches[0].fit_score > 0.9


def test_get_capability_returns_code_tests_and_agent_instructions():
    detail = get_capability("fastapi-safe-file-validation")

    assert detail is not None
    roles = {file.role for file in detail.files}
    assert {"core", "unit_test"}.issubset(roles)
    assert detail.instructions_for_agent
    assert detail.unit_test is not None
    assert "pytest" in detail.unit_test.command


def test_bundle_matches_each_platform_provided_task_and_marks_integration_test_external():
    bundle = build_bundle(
        BundleRequest(goal="给我的 FastAPI 项目加一个安全文件上传功能", language="python", framework="fastapi")
    )

    matched = [result for result in bundle.results if result.status == "matched"]
    not_provided = [result for result in bundle.results if result.status == "not_provided"]
    assert len(matched) >= 5
    assert not_provided
    assert not_provided[0].task.capability == "customer_project_integration_test"


def test_api_endpoints_cover_plan_search_get_and_bundle():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200

    plan = client.post(
        "/plan",
        json={"goal": "给我的 FastAPI 项目加一个安全文件上传功能", "language": "python", "framework": "fastapi"},
    )
    assert plan.status_code == 200
    assert len(plan.json()["tasks"]) >= 6

    search = client.post(
        "/search",
        json={"capability": "safe_file_validation", "language": "python", "framework": "fastapi"},
    )
    assert search.status_code == 200
    assert search.json()["matches"][0]["asset_id"] == "fastapi-safe-file-validation"

    capability = client.get("/capabilities/fastapi-safe-file-validation")
    assert capability.status_code == 200
    assert capability.json()["files"]

    bundle = client.post(
        "/bundle",
        json={"goal": "给我的 FastAPI 项目加一个安全文件上传功能", "language": "python", "framework": "fastapi"},
    )
    assert bundle.status_code == 200
    assert bundle.json()["results"]
