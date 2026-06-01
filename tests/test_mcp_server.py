from reuse_my_code.mcp_server import bundle_tool, get_tool, plan_tool, search_tool


def test_mcp_plan_tool_exposes_task_decomposition():
    result = plan_tool("给我的 FastAPI 项目加一个安全文件上传功能")

    assert result["tasks"]
    assert result["tasks"][0]["task_id"] == "auth_current_user"
    assert any(task["capability"] == "safe_file_validation" for task in result["tasks"])


def test_mcp_search_get_and_bundle_tools_return_agent_consumable_payloads():
    search = search_tool("safe_file_validation")
    assert search["matches"][0]["asset_id"] == "fastapi-safe-file-validation"

    detail = get_tool("fastapi-safe-file-validation")
    assert detail["files"]
    assert detail["unit_test"]["command"] == "pytest tests/test_file_validation.py"
    assert detail["instructions_for_agent"]

    bundle = bundle_tool("给我的 FastAPI 项目加一个安全文件上传功能")
    statuses = {result["task"]["task_id"]: result["status"] for result in bundle["results"]}
    assert statuses["file_validation"] == "matched"
    assert statuses["integration_test"] == "not_provided"


def test_mcp_get_tool_returns_error_for_unknown_asset():
    assert get_tool("missing-asset") == {"error": "capability not found", "asset_id": "missing-asset"}
