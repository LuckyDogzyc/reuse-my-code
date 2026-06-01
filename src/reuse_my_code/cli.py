from __future__ import annotations

import json

import typer

from .models import BundleRequest, PlanRequest, SearchRequest
from .planner import plan_tasks
from .registry import build_bundle, get_capability, search_capabilities

app = typer.Typer(help="Reuse My Code: task-level code capabilities for AI agents.")


def _print(data: object) -> None:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


@app.command()
def plan(goal: str, language: str = "python", framework: str = "fastapi") -> None:
    """Decompose a user coding goal into medium-grained reusable tasks."""
    _print(plan_tasks(PlanRequest(goal=goal, language=language, framework=framework)))


@app.command()
def search(capability: str, language: str = "python", framework: str = "fastapi") -> None:
    """Search capabilities for one task."""
    _print(search_capabilities(SearchRequest(capability=capability, language=language, framework=framework)))


@app.command("get")
def get_asset(asset_id: str) -> None:
    """Fetch code, tests, and instructions for one capability."""
    detail = get_capability(asset_id)
    if detail is None:
        raise typer.BadParameter(f"unknown asset_id: {asset_id}")
    _print(detail)


@app.command()
def bundle(goal: str, language: str = "python", framework: str = "fastapi") -> None:
    """Plan a goal and fetch matched task-level code capabilities."""
    _print(build_bundle(BundleRequest(goal=goal, language=language, framework=framework)))
