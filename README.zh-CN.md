# HTMlore

语言：[English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja.md)

部署：[自托管 Docker 与安全基线](DEPLOYMENT.zh-CN.md)

HTMlore 是一个自托管 HTML 知识库工作台，用于保存、浏览、阅读和未来通过 AI 讨论 HTML 形式的知识文件。它面向希望内容仍然保留为可携带文件、而不是被锁进数据库优先笔记软件的用户。

项目长期方向是一个 Web 优先的个人知识库：导入或生成 HTML 笔记，用集合和标签组织，通过精致的卡片工作台阅读，安装为 PWA，并在后续接入 AI 服务，对自己的资料库进行分类、检索、总结和多轮问答。

## 为什么是 HTMlore

很多知识工具要么把内容存成不透明的数据库记录，要么以 Markdown 写作为核心。HTMlore 选择另一条路线：

- **HTML 文件是长期内容层。** 笔记可以被检查、复制、归档、备份，也可以由普通 Web 基础设施托管。
- **YAML 旁车元数据让组织方式清晰可见。** 标题、摘要、集合、标签、收藏、归档和来源信息都与内容分离保存。
- **Web 应用是主客户端。** 项目目标是浏览器和移动端 PWA，而不是额外开发桌面端。
- **AI 是可选服务层。** 当前已经具备 AI 工作流的界面和上下文架构，但凭据与模型调用不会写入静态前端。

## 1.0.0 当前范围

当前 `1.0.0` 版本线面向本地、私有网络和自托管的真实使用：Docker 部署、内置登录、HTML 导入、元数据持久化、筛选、阅读、归档、公开分享，以及第一批服务端 AI 工作流。

当前已实现：

- 单容器 Docker 部署：`docker compose up -d --build`。
- Docker 镜像内置 `GET /api/health` 健康检查。
- 内置登录页，使用 HttpOnly session Cookie，测试用户由后端配置。
- 从 `app_static/` 生成的静态优先前端。
- 用于真实笔记本运行的后端 API。
- HTML 文件上传并导入到 `data/content`。
- YAML 元数据持久化到 `data/meta`。
- 导入、元数据变更和状态变更后自动重建 `public/`。
- 卡片式工作台，支持资料库、集合、标签、收藏、搜索和排序。
- 标签复选筛选，支持“或/且”匹配。
- 阅读页支持 iframe 阅读、原文访问、复制/分享、收藏/归档和元信息编辑。
- 非归档笔记支持手工 HTML 源码编辑和保守的可视化文件编辑，覆盖文本修改、文字/背景色、加粗/倾斜/下划线/删除线、撤销/重做、保存前分享安全预检和可收起编辑侧栏。
- 已归档笔记编辑锁定，并支持永久删除。
- 自托管多用户登录，用户名忽略大小写，并按用户隔离资料库数据。
- `data/users.json` 保存用户账号，密码以哈希形式存储。
- 新增用户的资料库保存到 `data/users/<data_id>/`。
- 资料库、集合、标签的侧栏显隐管理。
- 全局 AI 侧栏，支持工作区、集合、标签、阅读页和用户手动选择笔记等上下文。
- 服务端 AI 服务商配置，支持 OpenAI-compatible 接口。API key 只从后端环境变量读取，不允许通过浏览器设置接口提交或读取。
- 知识库问答已正式交付：支持上下文检索、当前上下文摘要、基于近期对话的追问理解、Markdown 回复渲染、可点击的外部来源引用、会话持久化、按当前上下文恢复最近会话和会话历史。
- 知识库问答运行时已拆分为 planner、search planner、answer、verifier、reviewer 等阶段，并暴露 agent/prompt trace，便于后续统一多智能体后端架构演进与排障。
- AI 回复支持严格模式与内容拓展模式。严格模式只基于当前资料库上下文回答；内容拓展模式预留外部来源检索，启用时必须返回明确来源。
- AI 运行记录、轻量异步生成历史、失败的对话生成任务重试，以及设置页中的全局 AI 会话管理。
- AI 生成历史支持 LangGraph 工作流详情、SSE 实时更新、阶段摘要、token 用量、轻量质量评分和脱敏运行元数据。
- 从 AI 对话生成 HTML 笔记的 beta 能力，采用 PM/UX/Coder/QA/Reviewer 分阶段图结构。
- 上传 HTML、Markdown 或纯文本资料生成 HTML 笔记的 beta 能力，先进行安全文本抽取，再复用 HTML 生成图结构。
- 关键词检索已落地，支持短问题查询拓展、多笔记证据均衡和检索覆盖诊断；已支持本地轻量向量索引，在 embedding 模型或向量索引未配置时自动回退到关键词检索。
- AI 护栏覆盖提示词长度、异常请求、疑似密钥输出和面向分享目标的 HTML 安全检查。
- 设置页包含 AI 服务商、数据、用户、账户安全、AI 会话历史、项目信息和更新相关区域。
- PWA manifest 与 Service Worker。
- 中文、英文、日语系统界面。
- 亮色/暗色主题切换和可调宽侧栏。
- `GET /api/version` 与 GitHub releases/tags 更新提示。
- 可选 Caddy Basic Auth 公网部署示例。

当前仍有限制或尚未实现：

- AI 生成、修改和知识库管理工作流仍处于 beta 阶段；知识库问答是 1.0.0 正式交付的 AI 工作流。
- 外部搜索已预留适配器，但暂未内置默认搜索服务商。
- vector / hybrid 检索需要在服务端配置 embedding 模型；未配置时会继续使用关键词检索。
- PDF 资料解析暂缓，后续会单独评估系统开销和方案。
- AI 重新分类、打标签等批处理任务。
- 云同步或托管订阅服务。
- 完整备份/恢复和 WebDAV 执行逻辑。
- 集合/标签批量重命名、合并、删除。

## Docker 快速开始

默认 Docker 路径适合本地电脑、NAS、局域网服务器或私有 VPS。它不需要 token，也不强制使用 Caddy。

`.env.example` 记录了可选的本地默认值，与 compose 默认值保持一致，仅用于本地或私有网络测试。

```bash
git clone https://github.com/JMoCoder/html_lore.git
cd html_lore
docker compose up -d --build
```

打开：

```text
http://localhost:8080
```

默认本地/测试登录账号：

```text
用户名：admin
密码：test-password
```

或在同一局域网的其他设备上打开：

```text
http://你的主机-ip:8080
```

运行时数据不会提交到 Git：

```text
data/content             默认管理员导入/生成的 HTML 文件
data/meta                默认管理员 YAML 元数据和运行时配置
data/users.json          自托管登录用户，密码为哈希值
data/users/<data_id>/    新增用户的 HTML、元数据、任务记录和 public 输出
public                   默认管理员生成后的 Web 应用输出
```

第一个由 env 引导的管理员会继续使用根目录 `data/content`、`data/meta` 和 `public`，用于兼容旧部署。后续新增用户会隔离到 `data/users/<data_id>/`。

新增一个自托管用户：

```bash
docker compose run --rm html-lore \
  html-lore user-add \
  --users-file /data/users.json \
  --username alice \
  --password "change-this-password"
```

用户名登录时忽略大小写；密码仍区分大小写，并以 PBKDF2 哈希保存，不保存明文。

不要使用默认账号把 compose 栈直接暴露到公网。公网部署时，必须修改 `HTML_LORE_AUTH_USERNAME`、`HTML_LORE_AUTH_PASSWORD` 和 `HTML_LORE_SESSION_SECRET`，并放在 HTTPS 后面。env 用户名/密码只会在 `data/users.json` 不存在时引导创建第一个管理员；之后以 `users.json` 为准。项目提供 Caddy Basic Auth 示例和生产取向 env 模板：`compose.prod.yml`、`.env.secure.example` 和 `deploy/caddy-basic-auth.Caddyfile`。

## 更新现有 Docker 部署

HTMlore 不会自动更新宿主机。应用只会根据 GitHub releases/tags 显示更新提示。

更新前先备份 `data/`：

```bash
cp -a data "data.backup.$(date +%Y%m%d-%H%M%S)"
```

查看版本差异：

```bash
git fetch
git log --oneline HEAD..origin/main
git diff --stat HEAD..origin/main
```

执行更新：

```bash
git pull --ff-only
docker compose up -d --build
docker compose logs -f
```

## 静态构建

HTMlore 也可以根据已有内容和元数据构建静态站点：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
html-lore build --content examples/content --meta examples/meta --out public
python -m http.server 8080 --directory public
```

打开 `http://localhost:8080`。

静态模式适合只读发布、类似 GitHub Pages 的托管，或检查生成后的应用。真实上传和元数据持久化需要后端 API 或默认 Docker 部署。公开 demo 会保持与正式工作台一致的界面风格，但后端与 AI 操作只作为静态预览展示，不接入真实处理链路。

## 数据模型

HTML 文件保存在内容目录下：

```text
content/
  generated/2026/05/mcp-security.html
  imported/docker-network.html
  reading/knowledge-workspace.html
```

可选元数据按相同路径保存在 `meta/items/` 下：

```yaml
id: generated/2026/05/mcp-security.html
title: MCP Server 安全模型
summary: 信任边界、权限、工具调用风险与部署建议。
source_type: topic
collection: AI
tags:
  - MCP
  - Security
favorite: true
pinned: true
open_mode: iframe
agent:
  generated: true
  job_id: job_demo
```

元数据会覆盖从 HTML 文档中提取的字段。没有元数据时，HTMlore 会推断标题、摘要、集合、来源类型、时间戳和审核状态。

## 后端 API

后端 API 已包含在 Docker 部署中，也可以通过可选 `agent` extra 手动启动：

```bash
pip install -e ".[agent]"
HTML_LORE_CONTENT=data/content \
HTML_LORE_META=data/meta \
HTML_LORE_PUBLIC=public \
html-lore serve-api --host 127.0.0.1 --port 8787
```

已实现接口：

- `GET /api/health`
- `GET /api/version`
- `GET /api/manifest`
- `GET /api/navigation`
- `PUT /api/navigation`
- `GET /api/items`
- `GET /api/search`
- `GET /api/items/{id}`
- `GET /api/items/{id}/content`
- `GET /api/items/{id}/raw`
- `POST /api/rebuild`
- `GET /api/rebuild/{job_id}`
- `PATCH /api/items/{id}/metadata`
- `PATCH /api/items/{id}/state`
- `POST /api/uploads/html`
- `GET /api/uploads/{upload_id}`
- `DELETE /api/items/{id}`
- `GET /api/ai/providers`
- `PUT /api/ai/providers`
- `GET /api/ai/status`
- `POST /api/ai/test-provider`
- `POST /api/ai/context/resolve`
- `POST /api/ai/conversations`
- `GET /api/ai/conversations`
- `GET /api/ai/conversations/latest`
- `GET /api/ai/conversations/{conversation_id}`
- `DELETE /api/ai/conversations/{conversation_id}`
- `GET /api/ai/conversations/{conversation_id}/messages`
- `POST /api/ai/conversations/{conversation_id}/messages`
- `POST /api/ai/conversations/{conversation_id}/generate-note`
- `POST /api/ai/conversations/{conversation_id}/generate-note/jobs`
- `POST /api/ai/material-runs`
- `POST /api/ai/material-jobs`
- `GET /api/ai/runs`
- `GET /api/ai/runs/{run_id}`
- `GET /api/ai/jobs`
- `GET /api/ai/jobs/{job_id}`
- `POST /api/ai/jobs/{job_id}/retry`
- `DELETE /api/ai/jobs/{job_id}`

API 覆盖当前前端核心流程：上传、列表、搜索、筛选、阅读、元信息编辑、收藏、归档、取消归档、已归档笔记永久删除、侧栏显隐持久化、重建任务、版本检查、AI 服务商状态检查、知识库问答、会话历史和 beta AI 笔记生成任务。

## AI 配置

AI 凭据必须放在服务端。前端设置页可以启用服务商、配置 base URL、模型和 embedding 模型引用，但不能提交或读取 API key。部署时通过环境变量配置：

```bash
HTML_LORE_AI_ENABLED=true
HTML_LORE_AI_PROVIDER=openai-compatible
HTML_LORE_AI_BASE_URL=https://your-newapi.example.com/v1
HTML_LORE_AI_MODEL=gpt-5.5
HTML_LORE_AI_EMBEDDING_MODEL=baai/bge-m3
HTML_LORE_AI_RETRIEVAL_MODE=hybrid
HTML_LORE_AI_API_KEY=replace-with-your-server-side-key
HTML_LORE_AI_GENERATION_ENGINE=v2
HTML_LORE_AI_GENERATION_MODEL=gpt-5.5
HTML_LORE_AI_GENERATION_MAX_TOKENS=12000
HTML_LORE_AI_GENERATION_JSON_MAX_TOKENS=5000
HTML_LORE_AI_GENERATION_HTML_MAX_TOKENS=12000
HTML_LORE_AI_PROVIDER_TIMEOUT_SECONDS=180
HTML_LORE_AI_GENERATION_JSON_TIMEOUT_SECONDS=180
HTML_LORE_AI_GENERATION_HTML_TIMEOUT_SECONDS=900
HTML_LORE_AI_EMBEDDING_TIMEOUT_SECONDS=45
```

部署注意事项：

- `HTML_LORE_AI_API_KEY` 只供服务端调用 chat 和 embedding，不要写入前端配置文件。
- `HTML_LORE_AI_EMBEDDING_MODEL` 用于启用 vector / hybrid 检索；embedding 模型或索引不可用时，HTMlore 会回退到关键词检索。
- `HTML_LORE_AI_QA_ENGINE=auto` 是默认问答引擎模式：优先使用 LangGraph
  工作流；如果 LangGraph 不可用，则回退到 `agent_runtime`。开发排查时可用
  `HTML_LORE_AI_QA_ENGINE=langgraph` 强制启用 LangGraph；需要稳定回退时可用
  `HTML_LORE_AI_QA_ENGINE=agent_runtime`。
- AI 生成与知识库问答共用服务商连接，但生成链路有独立模型、输出上限和
  节点级等待时间。`HTML_LORE_AI_GENERATION_MAX_TOKENS` 是兼容旧配置的通用生成上限；
  `HTML_LORE_AI_GENERATION_JSON_MAX_TOKENS` 控制 RequirementAnalyst / Planner /
  ContentWriter / StyleDesigner / Verifier / SafetyReviewer / Finalizer 等 JSON 节点；
  `HTML_LORE_AI_GENERATION_HTML_MAX_TOKENS` 控制 HTMLCoder。默认 chat provider 等待时间为
  `HTML_LORE_AI_PROVIDER_TIMEOUT_SECONDS=180` 秒；生成链路可用
  `HTML_LORE_AI_GENERATION_JSON_TIMEOUT_SECONDS` 和
  `HTML_LORE_AI_GENERATION_HTML_TIMEOUT_SECONDS` 单独覆盖，其中 HTMLCoder 默认 900 秒。
  embedding 请求仍使用 `HTML_LORE_AI_EMBEDDING_TIMEOUT_SECONDS=45` 秒。项目保留节点重试、
  最大图步数和 reviewer 修订轮次上限，但不设置整个生成任务的总耗时硬截断。
- 启用外部搜索时使用独立的服务端 key。Tavily 与 Brave 都是可选服务商，不配置时程序仍可按本地资料库和模型知识最低可用运行。
- smoke-test 命令会产生真实 provider 调用，只有确认当前环境模型和 key 都正确后再运行。

拓展模式可以使用 Tavily、Brave，或 Tavily 到 Brave 的链式回退作为受控外部搜索服务：

```bash
HTML_LORE_AI_EXTERNAL_SEARCH=tavily+brave
HTML_LORE_AI_EXTERNAL_SEARCH_API_KEY=replace-with-your-tavily-key
HTML_LORE_AI_EXTERNAL_SEARCH_BRAVE_API_KEY=replace-with-your-brave-key
HTML_LORE_AI_EXTERNAL_SEARCH_MAX_RESULTS=5
HTML_LORE_AI_EXTERNAL_SEARCH_DEPTH=basic
HTML_LORE_AI_EXTERNAL_SEARCH_AUTO_PARAMETERS=false
```

`HTML_LORE_AI_EXTERNAL_SEARCH` 可设为 `disabled`、`fake`、`tavily`、`brave` 或 `tavily+brave`。只配置 Tavily 或 Brave 任意一方即可启用外部检索；两者都配置时，HTMlore 会先用 Tavily，Tavily 不可用或无有效结果时再切换到 Brave，最后才回退到本地/关键词策略。

HTMlore 默认不使用搜索服务商生成的 answer，而是把 Tavily / Brave 作为外部证据检索工具，再由知识库问答 workflow 统一组织最终回答。搜索默认从低成本 `basic` 模式开始；遇到强时效、实体背景、多来源关系或用户明确要求详细核验时，会由搜索规划动态增加查询组合和结果上限。只有用户明确要求深度研究、多来源对比，或部署者显式配置时，才会升级到更高成本搜索参数。
像“联网搜索”这样的短追问，在进入搜索规划前会先继承最近一条用户问题，不再把上一轮 AI 回复正文拼进检索 query。

vector / hybrid 检索会在当前用户的 metadata 目录下保存轻量本地索引，例如 `meta/ai/vector_index.json`；多用户部署时则位于对应的 `users/{data_id}/meta/ai/vector_index.json`。这样可以在同一个应用进程中复用能力，同时保持用户工作台的逻辑隔离。

向量索引维护属于后台能力，不作为普通工作台按钮暴露。笔记被编辑、归档或永久删除后，HTMlore 会主动清理对应旧向量；部署者也可以在需要时通过 CLI 查看、清理或重建本地索引：

```bash
html-lore ai-vector-index stats
html-lore ai-vector-index prune
html-lore ai-vector-index rebuild
html-lore ai-vector-index smoke-test
```

`smoke-test` 会使用当前服务端配置的 provider 和 embedding 模型发起一次真实 embedding 请求。只有在确认该环境的模型与 key 都是预期配置后再运行。

开发测试时可以使用 `HTML_LORE_AI_PROVIDER=fake` 验证界面与会话流程，不会发起真实模型请求。公开状态接口只返回 `has_api_key`，不会返回密钥内容。

## 安全模型

默认 Docker 模式面向本地、局域网和私有自托管使用。默认本地/测试账号为 `admin` / `test-password`，并使用开发 session secret。浏览器会先进入登录页，登录后使用 HttpOnly session Cookie。当前不开放注册；生产部署必须替换默认用户名、密码和 session secret。自托管用户保存在 `data/users.json`；每个新增用户的资料库数据分别保存在 `data/users/<data_id>/`。

当你把 HTMlore 暴露到公网时：

- 必须放在 HTTPS 后面。
- 启用内置登录，或在前面放置等价认证边界。
- HTTPS 部署时设置 `HTML_LORE_SESSION_SECURE=true`。
- 为脚本、自动化或反向代理 API 访问设置 `HTML_LORE_API_TOKEN`。
- 不要把长期 API token 写进前端 JavaScript。
- 升级前和结构性变更前备份 `data/`。

详见 [DEPLOYMENT.zh-CN.md](DEPLOYMENT.zh-CN.md)，其中包含可复用安全基线和 Caddy Basic Auth 示例。

## 路线图

近期后端与笔记本能力：

- 集合和标签批量操作。
- 备份与恢复流程。
- WebDAV 设置执行。
- 更完整的导入校验和重复内容处理。
- 搜索后端升级路径，例如 SQLite FTS 或 Pagefind。

AI 能力：

- 提升问答检索质量，并接入真实 vector store 后端。
- 为内容拓展模式接入可配置外部搜索服务商。
- 优化 beta 多智能体 HTML 生成图，让规划、编码、QA 和审核逐步进入真实模型协作。
- AI 辅助分类、打标签、总结和清理任务。
- 对破坏性 AI 批处理提供用户确认和审计记录。

未来产品方向：

- 托管同步和跨设备使用。
- 用户账户与账户安全。
- 商业 AI/云服务集成。
- 更好的移动端 PWA 流程。
- 在保持本地优先数据所有权的前提下提供可选协作功能。

## 仓库结构

```text
app_static/        构建时复制到输出目录的静态工作台 UI
html_lore/        Python 构建器、manifest 逻辑和后端 API
examples/          示例内容与元数据
tests/             构建器和后端 API 测试
deploy/            可选部署示例
docs/              GitHub Pages 官网与只读 Demo
documents/         本地规划文档，Git 忽略
```

## 开发

```bash
pip install -e ".[dev,agent]"
pytest
python tests/run_smoke.py
npm ci
npm run test:e2e
html-lore build --content examples/content --meta examples/meta --out public
```

`npm run test:e2e` 使用本机已安装的 Chrome channel。CI 使用
`npm run test:e2e:ci` 和 Playwright 管理的 Chromium。GitHub Actions 会在
`develop`、`main` 和 Pull Request 上运行 pytest、Playwright Demo 检查和
`docker compose config`。

## 许可证

MIT
