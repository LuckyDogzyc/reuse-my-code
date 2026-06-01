# Reuse My Code

**Reusable task-level code capabilities for AI agents.**

Reuse My Code helps a user's coding agent decompose a broad development request into medium-grained engineering tasks, then retrieves reusable code, unit tests, and agent-facing integration instructions for each task. The first-stage MVP intentionally avoids platform-side LLM dependence: planning uses a small task-template catalog and retrieval uses structured metadata.

## Vision

Make coding easier for agents.

Today, coding agents depend heavily on the model's raw programming ability. Our long-term goal is to move part of that programming capability out of the model and into a reusable capability layer: tested code, unit tests, integration instructions, boundaries, dependency metadata, and verification reports that any agent can call.

Long-term direction:

1. **Task-level capability layer** — agents solve larger goals by composing medium-grained capabilities instead of generating everything from scratch.
2. **Lower token usage** — agents fetch known code and concise instructions rather than repeatedly generating long implementations.
3. **Boost weaker coding agents** — turn coding from pure code creation into task decomposition, retrieval, integration, and verification.
4. **Verified capability network** — over time, add community/enterprise contribution, usage telemetry, trust levels, and AI-assisted review without making LLM review a Phase 1 dependency.
5. **Agent-native interface** — expose capabilities through API, CLI, and eventually MCP so tools like Cursor, Claude Code, Codex, Hermes, and enterprise agents can use it.

## Phase 1 MVP

Phase 1 is **not** a user-upload-codebase product. It is a platform-maintained capability library.

Flow:

```text
User request
→ customer's AI uses our skill/CLI/API to plan medium-grained tasks
→ platform searches task-level capabilities
→ platform returns code + unit tests + instructions for each task
→ customer's AI integrates the returned code into the project
→ customer's AI runs unit tests and writes project-level integration tests
```

Example user request:

```text
给我的 FastAPI 项目加一个安全文件上传功能。
```

The plan endpoint decomposes it into tasks such as:

- current user dependency
- upload permission check
- file validation
- safe filename generation
- local file storage
- FastAPI upload route template
- integration test reminder

The platform returns results per task, not one giant generated implementation.

## What Phase 1 does

- Maintains a small curated library of task-level code capabilities.
- Provides `/plan`, `/search`, `/capabilities/{id}`, and `/bundle` APIs.
- Ships a `reuse` CLI for agents or humans.
- Returns code, unit tests, dependencies, boundaries, and agent instructions.
- Uses deterministic metadata matching rather than platform-side LLM calls.

## What Phase 1 does not do

- No user-uploaded full codebase analysis.
- No platform LLM review dependency.
- No public marketplace.
- No automatic trust certification.
- No automatic modification of customer projects.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
uvicorn reuse_my_code.api:app --reload
```

Try the CLI:

```bash
reuse plan "给我的 FastAPI 项目加一个安全文件上传功能" --language python --framework fastapi
reuse search safe_file_validation --language python --framework fastapi
reuse get fastapi-safe-file-validation
reuse bundle "给我的 FastAPI 项目加一个安全文件上传功能" --language python --framework fastapi
```

Try the API:

```bash
curl -s -X POST http://127.0.0.1:8000/plan   -H 'content-type: application/json'   -d '{"goal":"给我的 FastAPI 项目加一个安全文件上传功能","language":"python","framework":"fastapi"}' | python -m json.tool
```

## Repository layout

```text
src/reuse_my_code/
  api.py              # FastAPI API
  cli.py              # Typer CLI
  models.py           # Pydantic schemas
  planner.py          # deterministic task planner
  registry.py         # capability search/fetch/bundle service
  data/capabilities.yaml
  data/capabilities/  # code/test/instruction files returned by assets
tests/
```
