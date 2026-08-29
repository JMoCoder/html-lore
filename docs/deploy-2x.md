# HTMlore 2.0 独立部署与 1.x 迁移

当前稳定版 **2.0.0**（分支 `next`）。2.0 和冻结的 1.x（tag `v1.2.5`，分支 `main`）**并行、互不替换**。不要把 2.0 容器挂到正在运行的 1.x `data/` 上。

**没有传统数据库。** 笔记是磁盘上的 HTML + YAML sidecar + `users.json`。所谓「迁移」是复制文件库，不是 SQL dump。

## 分支约定

| 线 | Git | Docker | 端口（默认） | 状态 |
|---|---|---|---|---|
| 1.x | `main` / tag `v1.2.5` | 原 compose，服务名 `html-lore` | `8080→8787` | **冻结**，不再加功能 |
| 2.0 | `next` / tag `v2.0.0` | compose 项目 `html-lore-v2` | `3000→3000` | **当前稳定维护线** |

后续功能只合入 `next`。需要 1.x 时继续跑旧容器，或从 tag 检出旧树。

## 独立目录部署 2.0

建议新开主机目录，避免和 1.x 工作树混在一起：

```bash
git clone https://github.com/JMoCoder/html-lore.git /srv/html-lore-v2
cd /srv/html-lore-v2
git checkout next
cp .env.example .env
# 默认不启用应用内登录。公网用 Cloudflare Access / Caddy，不要依赖容器里的账号页。
docker compose up -d --build
```

打开 `http://localhost:3000`。空资料库会从镜像内 `examples/` 复制夹具。

compose 项目名固定为 `html-lore-v2`，容器名 `html-lore-v2`，默认端口 3000。只要 1.x 仍用 8080，两边可以同时在线。

## 从 1.x 拷贝资料库

1. 停写 1.x（或接受拷贝瞬间之后的增量不会带上）。
2. 备份 1.x `data/`。
3. 拷到 **新目录**，不要原地改 1.x 卷：

```bash
# 在 2.0 工作树里
npm run migrate:1x -- /srv/html-lore/data /srv/html-lore-v2/data
```

或：

```bash
node scripts/migrate-from-1x.mjs --dry-run /path/to/v1/data /path/to/v2/data
node scripts/migrate-from-1x.mjs /path/to/v1/data /path/to/v2/data
```

目标目录已有 HTML 时会拒绝覆盖；确认后加 `--force`。

| 复制 | 跳过（2.0 不用，避免把 AI 密钥/索引带进新栈） |
|---|---|
| `content/**/*.html` | `public/`（1.x 静态重建产物） |
| `meta/items/**/*.yml` | `meta/ai/`（会话、任务、向量索引） |
| `meta/config/shares.json` | `meta/config/jobs.json` |
| `meta/config/share-index.json` | `meta/config/ai_provider.json` |
| `meta/config/navigation.json` | 各用户下的 `public/` |
| `users.json` | |
| `users/<data_id>/{content,meta}` | |

分享 token 哈希仍在 `shares.json` / `share-index.json` 里，2.0 的 `/share/{token}` 可以继续打开未过期链接。YAML 里的 `agent:` 只读、界面不展示。

4. `.env` 里 `HTML_LORE_DATA` 指向拷贝后的目录（compose 默认 `./data`）。
5. `docker compose up -d --build` 后看 `GET /api/health` 是否返回 `"version":"2.0.0"`。

## 和 1.x 同时跑

- 不同宿主机目录、不同 compose 项目名、不同端口。
- **禁止**两个进程写同一份 `content/` / `meta/`。
- 1.x 的 `HTML_LORE_PUBLIC=/public` 静态卷 2.0 不需要；2.0 把用户侧 `public` 放在 `/data/public`。
- 2.0 不再提供 `/api/ai/*`、知识库问答、HTML 生成。迁过来等于放弃这些能力。

## 权限

compose 默认以宿主机 `1000:1000` 跑进程（与官方 `node` 镜像用户一致），这样 bind-mount 的 `./data` 可写。若宿主机 uid 不是 1000，在 `.env` 里设 `HTML_LORE_UID` / `HTML_LORE_GID`。

默认基础镜像是 `node:22-alpine`。本机拉不到 Docker Hub 时，可改用已有镜像，例如：

```bash
HTML_LORE_NODE_IMAGE=node:22-bullseye docker compose up -d --build
```

## 回滚

2.0 只读拷贝，1.x 目录未改。关掉 `html-lore-v2` 即可回到只使用 1.x。不要用 2.0 写过的拷贝覆盖回 1.x，除非你明确接受 2.0 的编辑结果。
