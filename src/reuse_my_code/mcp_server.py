from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .models import BundleRequest, PlanRequest, SearchRequest
from .planner import plan_tasks
from .registry import build_bundle, get_capability, search_capabilities

mcp = FastMCP("reuse-my-code")


def plan_tool(goal: str, language: str = "python", framework: str = "fastapi") -> dict[str, Any]:
    """Decompose a coding goal into medium-grained reusable tasks."""
    return plan_tasks(PlanRequest(goal=goal, language=language, framework=framework)).model_dump()


def search_tool(
    capability: str,
    language: str = "python",
    framework: str = "fastapi",
    task_id: str | None = None,
) -> dict[str, Any]:
    """Search task-level code capabilities by structured metadata."""
    return search_capabilities(
        SearchRequest(
            capability=capability,
            language=language,
            framework=framework,
            task_id=task_id,
        )
    ).model_dump()


def get_tool(asset_id: str) -> dict[str, Any]:
    """Fetch code, unit tests, dependencies, and agent instructions for one asset."""
    detail = get_capability(asset_id)
    if detail is None:
        return {"error": "capability not found", "asset_id": asset_id}
    return detail.model_dump()


def bundle_tool(goal: str, language: str = "python", framework: str = "fastapi") -> dict[str, Any]:
    """Plan a goal and fetch matched task-level capabilities in one call."""
    return build_bundle(BundleRequest(goal=goal, language=language, framework=framework)).model_dump()


mcp.tool(name="reuse_plan")(plan_tool)
mcp.tool(name="reuse_search")(search_tool)
mcp.tool(name="reuse_get")(get_tool)
mcp.tool(name="reuse_bundle")(bundle_tool)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
