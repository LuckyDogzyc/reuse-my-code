from __future__ import annotations

from html import escape

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .models import BundleRequest, PlanRequest, SearchRequest, VerifyRequest
from .planner import plan_tasks
from .registry import (
    build_bundle,
    get_capability,
    list_capabilities,
    search_capabilities,
    verify_usage,
)

app = FastAPI(
    title="Reuse My Code",
    version="0.1.0",
    description="Task-level reusable code capabilities for AI agents.",
)


def _home_html() -> str:
    capabilities = list_capabilities()
    cards = "\n".join(
        f"""
        <article class='card'>
          <h3>{escape(item.name)}</h3>
          <p>{escape(item.summary)}</p>
          <code>{escape(item.asset_id)}</code>
          <p><small>{escape(item.language)} / {escape(item.framework)} / {escape(item.capability)}</small></p>
        </article>
        """
        for item in capabilities
    )
    return f"""
    <!doctype html>
    <html lang='zh-CN'>
    <head>
      <meta charset='utf-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1' />
      <title>Reuse My Code</title>
      <style>
        body {{ font-family: Inter, system-ui, sans-serif; margin: 0; background: #0b1020; color: #edf2ff; }}
        main {{ max-width: 1080px; margin: 0 auto; padding: 56px 24px; }}
        .hero {{ padding: 40px; border: 1px solid #27345f; border-radius: 24px; background: linear-gradient(135deg, #111a33, #101827); }}
        h1 {{ font-size: 48px; margin: 0 0 12px; }}
        .tagline {{ font-size: 22px; color: #b8c7ff; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 24px; }}
        .card {{ border: 1px solid #27345f; border-radius: 16px; padding: 18px; background: #11182d; }}
        code {{ color: #96f2d7; word-break: break-all; }}
        a {{ color: #91a7ff; }}
      </style>
    </head>
    <body>
      <main>
        <section class='hero'>
          <h1>Reuse My Code</h1>
          <p class='tagline'>Make coding easier for agents.</p>
          <p>客户 AI 先把需求拆成中等粒度 task，再针对每个 task 获取平台返回的 code、unit test 和 instructions，从而少生成、多复用。</p>
          <p><a href='/docs'>OpenAPI Docs</a> · <a href='/capabilities'>Capabilities JSON</a></p>
        </section>
        <section>
          <h2>Starter goals</h2>
          <div class='grid'>
            <article class='card'><h3>FastAPI 安全文件上传</h3><code>给我的 FastAPI 项目加一个安全文件上传功能</code></article>
            <article class='card'><h3>FastAPI 分页查询</h3><code>给我的 FastAPI 项目加一个分页查询接口</code></article>
          </div>
        </section>
        <section>
          <h2>Capability library</h2>
          <div class='grid'>{cards}</div>
        </section>
      </main>
    </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return _home_html()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/plan")
def plan(request: PlanRequest):
    return plan_tasks(request)


@app.post("/search")
def search(request: SearchRequest):
    return search_capabilities(request)


@app.get("/capabilities")
def capabilities():
    return {"capabilities": list_capabilities()}


@app.get("/capabilities/{asset_id}")
def capability(asset_id: str):
    detail = get_capability(asset_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="capability not found")
    return detail


@app.post("/bundle")
def bundle(request: BundleRequest):
    return build_bundle(request)


@app.post("/verify")
def verify(request: VerifyRequest):
    return verify_usage(request)
