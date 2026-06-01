from __future__ import annotations

from reuse_my_code.models import BundleRequest
from reuse_my_code.registry import build_bundle


def print_bundle(goal: str) -> None:
    bundle = build_bundle(BundleRequest(goal=goal, language="python", framework="fastapi"))
    print(f"Goal: {bundle.goal}")
    for result in bundle.results:
        asset = result.selected.asset_id if result.selected else "-"
        print(f"- {result.task.task_id}: {result.status} -> {asset}")
        if result.selected and result.selected.unit_test:
            print(f"  test: {result.selected.unit_test.command}")


def main() -> None:
    print_bundle("给我的 FastAPI 项目加一个分页查询接口")


if __name__ == "__main__":
    main()
