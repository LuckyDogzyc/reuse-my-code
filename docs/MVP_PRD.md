# Reuse My Code MVP PRD v0.1

## 1. Product thesis

用户的 AI Agent 不应该每次都从零生成代码。第一阶段，Reuse My Code 提供平台维护的 task-level code capabilities：客户 AI 先把用户需求拆成中等粒度任务，再对每个 task 获取平台返回的 code、unit test 和 instructions，最后由客户 AI 集成进项目。

## 2. First user story

用户说：

> 给我的 FastAPI 项目加一个安全文件上传功能。

客户 AI 使用我们的 Skill/API：

1. `plan`：拆成中等粒度任务。
2. `search`：针对每个 task 搜索代码能力。
3. `get`：获取 code + unit test + agent instructions。
4. 客户 AI 集成代码。
5. 客户 AI 运行平台提供的 unit tests。
6. 客户 AI 根据项目上下文补 integration test。

## 3. Why task-level decomposition matters

直接搜索“安全文件上传”太大，难以命中刚好适配的代码，也会导致返回代码过长、token 成本高、集成失败率高。

中等粒度 task 更稳定：

- current user dependency
- permission check
- safe file validation
- safe filename generation
- local file storage
- upload route template
- project-level integration test reminder

每个 task 对应一个较小、可测试、可组合的 capability。

## 4. Phase 1 scope

### In scope

- 平台维护能力库。
- Deterministic task planner，先覆盖 FastAPI 安全文件上传模板。
- Structured metadata search，不依赖平台 LLM。
- 返回 code、unit test、dependencies、boundaries、instructions_for_agent。
- API + CLI + stdio MCP server.
- MVP 测试覆盖 plan/search/get/bundle 和 MCP tool wrappers。

### Out of scope

- 用户上传完整代码库。
- 平台 LLM 审核。
- 自动拆解客户 repo。
- 公共 marketplace。
- 企业私有库。
- 自动修改客户项目。
- 官方可信认证。

## 5. Long-term goal

Make coding easier for agents.

长期目标不是做一个普通代码片段库，而是把一部分软件工程能力外置成 Agent 可调用的能力层。未来可以逐步加入：

1. 更多语言和框架。
2. 更丰富 task template。
3. MCP server。
4. 使用数据和成功率反馈。
5. 社区贡献小型 capability。
6. 企业私有 capability library。
7. AI-assisted review，但不作为第一阶段依赖。
8. Trust graph / capability graph。

## 6. Phase 1 success metrics

- 一个常见需求能被拆成 5+ 中等粒度任务。
- 每个可提供 task 能返回可读 code 和 unit test。
- 客户 AI 可以用 bundle 输出完成集成上下文，而不是从零生成。
- 相比完整生成，返回内容更结构化、可缓存、可复用。
