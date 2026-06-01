from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .models import (
    BundleRequest,
    BundleResponse,
    CapabilityDetail,
    CapabilityFile,
    CapabilitySummary,
    PlanRequest,
    SearchRequest,
    SearchResponse,
    TaskResult,
    UnitTestInfo,
)
from .planner import plan_tasks

DATA_DIR = Path(__file__).parent / "data"
CAPABILITY_FILE = DATA_DIR / "capabilities.yaml"


@lru_cache(maxsize=1)
def load_registry() -> list[dict[str, Any]]:
    with CAPABILITY_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("capabilities", [])


def _score(capability: dict[str, Any], request: SearchRequest) -> float:
    score = 0.0
    if capability["capability"] == request.capability:
        score += 0.65
    elif request.capability in capability.get("provides", []):
        score += 0.45
    else:
        return 0.0
    if capability["language"].lower() == request.language.lower():
        score += 0.18
    if capability["framework"].lower() == request.framework.lower():
        score += 0.17
    return round(min(score, 1.0), 2)


def search_capabilities(request: SearchRequest) -> SearchResponse:
    matches: list[CapabilitySummary] = []
    for item in load_registry():
        fit_score = _score(item, request)
        if fit_score <= 0:
            continue
        matches.append(
            CapabilitySummary(
                asset_id=item["asset_id"],
                version=str(item["version"]),
                name=item["name"],
                summary=item["summary"],
                language=item["language"],
                framework=item["framework"],
                capability=item["capability"],
                fit_score=fit_score,
                risk_level=item.get("risk_level", "medium"),
                provides=item.get("provides", []),
                does_not_provide=item.get("does_not_provide", []),
            )
        )
    matches.sort(key=lambda item: item.fit_score, reverse=True)
    return SearchResponse(matches=matches)


def get_capability(asset_id: str) -> CapabilityDetail | None:
    item = next((entry for entry in load_registry() if entry["asset_id"] == asset_id), None)
    if item is None:
        return None

    files = []
    for file_spec in item.get("files", []):
        path = DATA_DIR / "capabilities" / asset_id / file_spec["source"]
        files.append(
            CapabilityFile(
                path=file_spec["target_path"],
                role=file_spec["role"],
                content=path.read_text(encoding="utf-8"),
            )
        )

    unit_test = None
    if test := item.get("unit_test"):
        unit_test = UnitTestInfo(command=test["command"], covers=test.get("covers", []))

    return CapabilityDetail(
        asset_id=item["asset_id"],
        version=str(item["version"]),
        name=item["name"],
        summary=item["summary"],
        language=item["language"],
        framework=item["framework"],
        capability=item["capability"],
        fit_score=1.0,
        risk_level=item.get("risk_level", "medium"),
        provides=item.get("provides", []),
        does_not_provide=item.get("does_not_provide", []),
        files=files,
        dependencies=item.get("dependencies", []),
        instructions_for_agent=item.get("instructions_for_agent", []),
        config_schema=item.get("config_schema", {}),
        unit_test=unit_test,
    )


def build_bundle(request: BundleRequest) -> BundleResponse:
    plan = plan_tasks(PlanRequest(**request.model_dump()))
    results: list[TaskResult] = []
    reminders: list[str] = []
    for task in plan.tasks:
        if not task.provided_by_platform:
            reminders.append(
                "根据客户项目实际 auth/session/database/storage 编写项目级 integration test。"
            )
            results.append(
                TaskResult(
                    task=task,
                    selected=None,
                    status="not_provided",
                    message="平台第一阶段只提供 task-level code capability 和 unit test；该项由客户 AI 编写。",
                )
            )
            continue
        search = search_capabilities(
            SearchRequest(
                task_id=task.task_id,
                capability=task.capability,
                language=task.language,
                framework=task.framework,
            )
        )
        if not search.matches:
            results.append(TaskResult(task=task, selected=None, status="not_found"))
            continue
        detail = get_capability(search.matches[0].asset_id)
        results.append(TaskResult(task=task, selected=detail, status="matched"))
    return BundleResponse(goal=request.goal, results=results, integration_test_reminders=reminders)
