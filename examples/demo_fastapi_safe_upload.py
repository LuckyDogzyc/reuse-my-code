from __future__ import annotations

from reuse_my_code.models import BundleRequest
from reuse_my_code.registry import build_bundle


def main() -> None:
    bundle = build_bundle(
        BundleRequest(
            goal="给我的 FastAPI 项目加一个安全文件上传功能",
            language="python",
            framework="fastapi",
        )
    )
    print(f"Goal: {bundle.goal}")
    for result in bundle.results:
        task = result.task
        asset = result.selected.asset_id if result.selected else "-"
        print(f"- {task.task_id}: {result.status} -> {asset}")
        if result.selected and result.selected.unit_test:
            print(f"  test: {result.selected.unit_test.command}")
    if bundle.integration_test_reminders:
        print("Integration test reminders:")
        for reminder in bundle.integration_test_reminders:
            print(f"- {reminder}")


if __name__ == "__main__":
    main()
