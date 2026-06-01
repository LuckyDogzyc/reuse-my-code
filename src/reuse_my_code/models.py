from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProjectContext(BaseModel):
    language: str = "python"
    framework: str = "fastapi"
    auth: str | None = None
    storage: str | None = None


class PlanRequest(BaseModel):
    goal: str
    language: str = "python"
    framework: str = "fastapi"
    project_context: ProjectContext | None = None


class Task(BaseModel):
    task_id: str
    title: str
    capability: str
    language: str
    framework: str
    required: bool = True
    provided_by_platform: bool = True
    rationale: str | None = None


class PlanResponse(BaseModel):
    goal: str
    tasks: list[Task]
    notes_for_agent: list[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    capability: str
    language: str = "python"
    framework: str = "fastapi"
    task_id: str | None = None


class CapabilitySummary(BaseModel):
    asset_id: str
    version: str
    name: str
    summary: str
    language: str
    framework: str
    capability: str
    fit_score: float
    risk_level: Literal["low", "medium", "high"] = "medium"
    provides: list[str] = Field(default_factory=list)
    does_not_provide: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    matches: list[CapabilitySummary]


class CapabilityFile(BaseModel):
    path: str
    role: Literal["core", "unit_test", "instructions", "example"]
    content: str


class UnitTestInfo(BaseModel):
    command: str
    covers: list[str] = Field(default_factory=list)


class CapabilityDetail(CapabilitySummary):
    files: list[CapabilityFile]
    dependencies: list[str] = Field(default_factory=list)
    instructions_for_agent: list[str] = Field(default_factory=list)
    config_schema: dict = Field(default_factory=dict)
    unit_test: UnitTestInfo | None = None


class TaskResult(BaseModel):
    task: Task
    selected: CapabilityDetail | None = None
    status: Literal["matched", "not_found", "not_provided"]
    message: str | None = None


class BundleRequest(PlanRequest):
    pass


class BundleResponse(BaseModel):
    goal: str
    results: list[TaskResult]
    integration_test_reminders: list[str] = Field(default_factory=list)
