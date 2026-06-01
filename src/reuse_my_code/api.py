from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .models import BundleRequest, PlanRequest, SearchRequest
from .planner import plan_tasks
from .registry import build_bundle, get_capability, search_capabilities

app = FastAPI(
    title="Reuse My Code",
    version="0.1.0",
    description="Task-level reusable code capabilities for AI agents.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/plan")
def plan(request: PlanRequest):
    return plan_tasks(request)


@app.post("/search")
def search(request: SearchRequest):
    return search_capabilities(request)


@app.get("/capabilities/{asset_id}")
def capability(asset_id: str):
    detail = get_capability(asset_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="capability not found")
    return detail


@app.post("/bundle")
def bundle(request: BundleRequest):
    return build_bundle(request)
