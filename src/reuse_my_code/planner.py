from __future__ import annotations

from .models import PlanRequest, PlanResponse, Task


FASTAPI_SAFE_UPLOAD_TASKS = [
    ("auth_current_user", "确认当前登录用户依赖", "current_user_dependency", True),
    ("upload_permission", "上传权限检查", "permission_check", True),
    ("file_validation", "文件类型、大小和 MIME 校验", "safe_file_validation", True),
    ("safe_filename", "安全文件名生成，防止路径穿越", "safe_filename_generation", True),
    ("local_storage", "文件保存到本地目录", "local_file_storage", True),
    ("upload_route", "FastAPI 上传接口路由模板", "fastapi_upload_route", True),
    ("integration_test", "项目级集成测试提醒", "customer_project_integration_test", False),
]

FASTAPI_PAGINATION_TASKS = [
    ("pagination_params", "分页参数校验", "pagination_params", True),
    ("sqlalchemy_pagination", "SQLAlchemy offset/limit 分页查询", "sqlalchemy_pagination", True),
    ("paginated_response", "分页响应结构", "paginated_response_schema", True),
    ("pagination_route", "FastAPI 分页接口路由模板", "fastapi_pagination_route", True),
    ("integration_test", "项目级集成测试提醒", "customer_project_integration_test", False),
]


def plan_tasks(request: PlanRequest) -> PlanResponse:
    """Deterministic Phase-1 planner.

    Phase 1 intentionally avoids platform-side LLM planning. The customer's agent can
    call this as a structured decomposition helper. We start with a small template
    catalog and return medium-grained tasks that can match code capabilities.
    """

    goal_lower = request.goal.lower()
    framework = (request.framework or request.project_context.framework if request.project_context else request.framework).lower()
    language = (request.language or request.project_context.language if request.project_context else request.language).lower()

    is_upload = any(token in goal_lower for token in ["upload", "上传", "file", "文件"])
    is_pagination = any(token in goal_lower for token in ["pagination", "paginate", "分页", "page", "limit"])
    is_fastapi = framework == "fastapi" or "fastapi" in goal_lower

    if language == "python" and is_fastapi and is_pagination:
        tasks = [
            Task(
                task_id=task_id,
                title=title,
                capability=capability,
                language="python",
                framework="fastapi",
                required=True,
                provided_by_platform=provided,
                rationale="分页查询需要按参数校验、查询、响应结构、路由模板拆分，逐 task 检索代码。",
            )
            for task_id, title, capability, provided in FASTAPI_PAGINATION_TASKS
        ]
        return PlanResponse(
            goal=request.goal,
            tasks=tasks,
            notes_for_agent=[
                "先复用分页参数、查询 helper 和响应 schema，再接入项目路由。",
                "平台提供 task-level unit test；项目级 integration test 由客户 AI 根据真实模型和数据库编写。",
                "不要把分页 helper 绑定到单一 ORM model，保持中等粒度可复用。",
            ],
        )

    if language == "python" and is_fastapi and is_upload:
        tasks = [
            Task(
                task_id=task_id,
                title=title,
                capability=capability,
                language="python",
                framework="fastapi",
                required=True,
                provided_by_platform=provided,
                rationale="安全文件上传需要按中等粒度能力拆分，逐 task 检索代码。",
            )
            for task_id, title, capability, provided in FASTAPI_SAFE_UPLOAD_TASKS
        ]
        return PlanResponse(
            goal=request.goal,
            tasks=tasks,
            notes_for_agent=[
                "先按 task 获取平台返回的代码能力，不要一次性生成完整功能。",
                "每个 task 的 unit test 来自平台；项目级 integration test 由客户 AI 根据项目上下文编写。",
                "集成时保留 core 文件的安全逻辑，优先只改 adapter/route 层。",
            ],
        )

    return PlanResponse(
        goal=request.goal,
        tasks=[
            Task(
                task_id="generic_capability_search",
                title="通用能力检索",
                capability="generic_code_capability",
                language=language,
                framework=framework,
                rationale="当前 MVP 暂无专用模板，使用通用能力检索。",
            )
        ],
        notes_for_agent=["当前 MVP 主要覆盖 Python/FastAPI 安全文件上传和分页查询场景。"],
    )
