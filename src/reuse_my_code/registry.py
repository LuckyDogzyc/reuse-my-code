from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
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
    VerifyRequest,
    VerifyResponse,
    FileVerification,
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


def _content_hash(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def verify_usage(request: VerifyRequest) -> VerifyResponse:
    detail = get_capability(request.asset_id)
    if detail is None:
        return VerifyResponse(
            asset_id=request.asset_id,
            project_path=request.project_path,
            status="not_found",
            message="capability not found",
        )

    project_root = Path(request.project_path).expanduser().resolve()
    files: list[FileVerification] = []
    for expected in detail.files:
        actual_path = (project_root / expected.path).resolve()
        expected_sha = _content_hash(expected.content)
        exists = actual_path.exists() and actual_path.is_file()
        actual_sha = _file_hash(actual_path) if exists else None
        files.append(
            FileVerification(
                path=expected.path,
                role=expected.role,
                exists=exists,
                expected_sha256=expected_sha,
                actual_sha256=actual_sha,
                hash_match=actual_sha == expected_sha,
            )
        )

    if all(file.hash_match for file in files):
        status = "verified"
        message = "all capability files match platform-provided content"
    elif any(not file.exists for file in files):
        status = "missing"
        message = "one or more capability files are missing"
    else:
        status = "modified"
        message = "all files exist, but one or more hashes differ from platform-provided content"

    return VerifyResponse(
        asset_id=detail.asset_id,
        project_path=str(project_root),
        status=status,
        files=files,
        unit_test_command=detail.unit_test.command if detail.unit_test else None,
        message=message,
    )
