# HTMlore 2.0

自托管 HTML 知识工作台：**导入、筛选、阅读、编辑、分享**。笔记仍是磁盘上的 HTML + YAML，没有 SQL 数据库。

当前稳定版是 **2.0.9**，维护线在 **`main`**。1.x（tag `v1.2.5`，分支 `legacy`）**冻结**，不再加功能。2.0 用独立 Docker 服务部署，不替换正在运行的 1.x。

```bash
npm install
npm run dev
npm test
```

打开：

- 工作台 `http://localhost:3000`
- 阅读 `http://localhost:3000/read/generated/2026/05/mcp-security.html`
- 安全分享 `http://localhost:3000/share/<token>`
- 静态 demo（GitHub Pages，只读、无后端）https://jmocoder.github.io/html-lore/demo/

站点根 `https://jmocoder.github.io/html-lore/` 是营销首页，另有任务维护；在那之前根路径可能仍是 404，先看 `/demo/`。

## 自托管鉴权

2.0 **默认没有应用内登录**。不要把工作台直接暴露到公网；在入口用 Cloudflare Access、Caddy 或其他反代做鉴权。只有显式设置 `HTML_LORE_SESSION_SECRET` 和账号时，才会出现 1.x 那套登录页。

## Docker（独立于 1.x）

1.x 默认 `8080`；2.0 compose 项目名是 `html-lore-v2`，默认 **`3000`**。两边可以同时在线，但必须使用**不同的数据目录**。

```bash
cp .env.example .env
docker compose up --build
```

数据挂载到 `./data`（`content/`、`meta/`、`users.json`）。空库会从镜像内 `examples/` 复制夹具。

从冻结的 1.x 拷贝笔记（复制文件，不是数据库 dump）：

```bash
npm run migrate:1x -- /srv/html-lore/data ./data
# 无登录单库：把 1.x 多账户摊进根目录
npm run migrate:1x -- --merge-users /srv/html-lore/data ./data
```

完整步骤、跳过 AI/静态产物清单、并行运行注意见 [`docs/deploy-2x.md`](docs/deploy-2x.md)。1.x 数据契约见 [`docs/compat-1x.md`](docs/compat-1x.md)。

## 架构

- `src/app/` — Next.js 路由与 Route Handlers（**API 路径与 1.x 对齐**）
- `src/features/` — 工作台 / 阅读 / 分享 / 设置 UI
- `src/server/` — 纯 TypeScript 领域层（不 import `next/*`）
- `scripts/migrate-from-1x.mjs` — 1.x → 2.0 文件库拷贝

2.0 不包含知识库问答和 HTML 生成。1.x 实现仍在 `legacy` / tag `v1.2.5`。
