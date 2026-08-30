# HTMlore 1.x → 2.0 数据契约

2.0 重写 UI 与运行时，**用户资产仍是磁盘文件**。本文件描述 2.0 必须兼容读写的 1.x 契约（来源 tag `v1.2.5`）。

## 目录布局

| 路径 | 含义 |
|---|---|
| `content/**/*.html` | 笔记正文；`item id` = 相对路径 |
| `meta/items/**/*.yml` | sidecar 元数据；路径把 `.html` 换成 `.yml` |
| `meta/config/shares.json` | 分享记录（只存 token hash） |
| `meta/config/share-index.json` | 根级 token → `data_id` 索引 |
| `data/users.json` | 用户表 |
| `data/users/<data_id>/{content,meta,public}` | 非 default 用户隔离 |

环境变量前缀 **`HTML_LORE_`**（无 `DATA_DIR`）：

- `CONTENT` / `META` / `PUBLIC` / `TITLE`
- `SESSION_SECRET` + `AUTH_USERNAME`/`AUTH_PASSWORD` 或 `users.json`
- `USERS_FILE` / `USER_DATA_DIR`
- `MAX_UPLOAD_BYTES` / `SHARE_INTERACTIVE_ENABLED`

## Item 字段

与 1.x manifest item 对齐：`id`, `title`, `summary`, `path`, `source_type`, `collection`, `tags`, `favorite`, `archived`, `pinned`, `created`, `updated`, `open_mode`, `agent` 等。

- `generated/` → `source_type: topic`
- `imported/` → `source_type: imported`
- 其它 → `source_type: html`
- YAML 的 `agent:` 只兼容读取，2.0 UI 不展示 AI 入口

## HTTP API（2.0 保留，路径不变）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| GET/POST | `/api/auth/status` / `login` / `logout` | 会话 |
| GET | `/api/items` | 列表/筛选（query 同 1.x） |
| GET | `/api/search` | 元数据搜索 |
| GET | `/api/manifest` | manifest v2 |
| GET/PUT/PATCH/DELETE | `/api/items/{id}/...` | 读/写正文、元数据、状态、删除 |
| POST | `/api/uploads/html` | 导入 HTML |
| GET/POST | `/api/shares` | 列表/创建 |
| PATCH/DELETE | `/api/shares/{share_id}` | 更新/撤销 |
| GET | `/api/public/shares/{token}` | 公开只读 JSON |
| GET | `/share/{token}` | 公开分享页（2.0 为 Next 路由） |

**2.0 永久移除**：全部 `/api/ai/*`、知识库问答、HTML 生成、AI 设置。

## 分享安全

- **safe**：消毒静态副本；不可直享则写 `{stem}--safe-share.html`
- **interactive**：iframe `sandbox="allow-scripts"`（无 same-origin）
- token 明文只在创建响应出现；store 存 sha256
- 分享页 **`force-dynamic`**，禁止 CDN/Full Route Cache

## 独立部署与迁移

2.0 以独立 Docker 服务运行，**不要原地替换 1.x 容器或挂载正在使用的 1.x `data/`**。步骤、跳过清单和并行运行注意见 [`docs/deploy-2x.md`](deploy-2x.md)。

```bash
npm run migrate:1x -- /path/to/v1/data /path/to/v2/data
# 无登录部署把多账户并入根库时加 --merge-users
docker compose up --build
```

## 本地开发

首次启动且 `content/` 为空时，2.0 会自动从 `examples/` 复制夹具（与 1.x examples 相同）。

```bash
npm install
npm run dev
```

2.0 **默认不启用应用内登录**。只有显式设置 `HTML_LORE_SESSION_SECRET` 以及账号（或已有 `users.json`）时才会出现登录页。公网请用反代鉴权。

可选鉴权（1.x 兼容，需自行打开）：

```bash
export HTML_LORE_SESSION_SECRET=dev-secret
export HTML_LORE_AUTH_USERNAME=admin
export HTML_LORE_AUTH_PASSWORD=test-password
```
