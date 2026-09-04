# HTMlore 2.0 独立部署与 1.x 迁移

当前稳定版 **2.0.9**（分支 `main`）。2.0 和冻结的 1.x（tag `v1.2.5`，分支 `legacy`）**并行、互不替换**。不要把 2.0 容器挂到正在运行的 1.x `data/` 上。

**没有传统数据库。** 笔记是磁盘上的 HTML + YAML sidecar + `users.json`。所谓「迁移」是复制文件库，不是 SQL dump。

## 分支约定

| 线 | Git | Docker | 端口（默认） | 状态 |
|---|---|---|---|---|
| 1.x | `legacy` / tag `v1.2.5` | 原 compose，服务名 `html-lore` | `8080→8787` | **冻结**，不再加功能 |
| 2.0 | `main` / tag `v2.0.9` | compose 项目 `html-lore-v2` | `3000→3000` | **当前稳定维护线** |

后续功能只合入 `main`。需要 1.x 时继续跑旧容器，或从 `legacy` / tag `v1.2.5` 检出旧树。

## 独立目录部署 2.0

建议新开主机目录，避免和 1.x 工作树混在一起：

```bash
git clone https://github.com/JMoCoder/html-lore.git /srv/html-lore-v2
cd /srv/html-lore-v2
cp .env.example .env
# 默认不启用应用内登录。公网用 Cloudflare Access / Caddy，不要依赖容器里的账号页。
docker compose up -d --build
```

打开 `http://localhost:3000`。空资料库会从镜像内 `examples/` 复制夹具。

不想先装 Docker 时，可以看只读静态预览：https://jmocoder.github.io/html-lore/demo/ （无登录、无 AI、不能导入或保存）。营销首页在仓库 `docs/index.html`，由单独任务维护。

compose 项目名固定为 `html-lore-v2`，容器名 `html-lore-v2`，默认 **`127.0.0.1:3000`**。只要 1.x 仍用 8080，两边可以同时在线。公网走本机 Caddy 反代，不要把应用端口绑到 `0.0.0.0`（UFW 挡着也不算过关）。局域网直连才设 `HTML_LORE_HTTP_BIND=0.0.0.0`。

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

**无登录单库**（2.0 默认）只读数据根目录的 `content/` / `meta/`。1.x 若有多个 `users/<id>/`，默认拷贝会把这些笔记留在 `users/` 下，无登录模式看不见。要并入根库：

```bash
node scripts/migrate-from-1x.mjs --merge-users /path/to/v1/data /path/to/v2/data
```

`--merge-users` 会把 `users/<id>/{content,meta}` 摊到目标根目录，不带 `users.json` / `meta/ai`，合并 `shares.json`，并把 `share-index.json` 的 `data_id` 改成 `default`（无该文件时 `settingsForShareToken` 本来就回落到根库）。默认剔除 1.x 的 `AI生成` 标签，可用 `--strip-tags=a,b` 改名单，或 `--strip-tags=` 关闭。同一相对路径在根库和某用户库同时存在时会中止，需先手工处理。

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
5. `docker compose up -d --build` 后看 `GET /api/health` 是否返回 `"version":"2.0.9"`。

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

## 反代鉴权与公开路径

公网入口用 Caddy / Cloudflare Access 包住工作台。应用本身不拦静态文件；401 来自反代。分享页 `/share/{token}` 和 `/api/public/shares/{token}` 必须豁免，否则无凭据打不开。

分享页**不再请求** PWA 壳（`/manifest.webmanifest`、`/icons/*`、`/favicon.ico`、`/html-lore-logo.svg`、`/sw.js`）。访客读的是一篇笔记，不是可安装的工作台；把这些品牌资源留在鉴权区即可。标签栏图标用内联 SVG（data URI），不额外打这些路径。若运维仍要在分享页加载图标文件，再在 Caddy 追加豁免——那会把品牌资源公开。

Caddy 里「豁免 + 鉴权」必须用**兄弟互斥 `handle`**，不要把 named matcher 嵌进鉴权 `handle`。嵌套时豁免路径仍会掉进鉴权。

分享打不开时，按四道闸门复刻比读代码快：`record`（token hash 在 `shares.json`）→ `active`（未撤销、未过期）→ `item`（根库能读到、ID 未改、未归档）→ `content`（`content_item_id` 对应的 HTML 还在）。无登录迁移后若源库没有 `share-index.json`，不影响根级解析。

## 现场升级（rain：`/opt/html-lore-v2`）

未写出备份不得换 tag 或 `compose up --build`。目录：

```bash
TAG=$(git -C /opt/html-lore-v2 describe --tags --always)
TS=$(date +%Y%m%d-%H%M%S)
DEST=/opt/backups/html-lore-v2-upgrade-$TAG-$TS
mkdir -p "$DEST"
tar -C /opt/html-lore-v2 -czf "$DEST/data-$TAG.tar.gz" data
install -m 600 /opt/html-lore-v2/.env "$DEST/env.snapshot"
cp /opt/html-lore-v2/docker-compose.yml "$DEST/docker-compose.yml"
(cd "$DEST" && sha256sum data-*.tar.gz env.snapshot docker-compose.yml > SHA256SUMS)
```

快照至少包含 **data + .env + compose**。2026-08-30 升 2.0.3 时漏了这步，靠当日 12:33 的 `/opt/backups/html-lore-v2-migration-*` 兜底。

然后才 `git fetch --tags`、检出目标 tag、确认 compose 仍是 `127.0.0.1:…:3000`（或 `HTML_LORE_HTTP_BIND` 默认 loopback），再 `docker compose up -d --build`。不要重跑迁移，不要动 `/opt/html-lore`。

## 回滚

2.0 只读拷贝，1.x 目录未改。关掉 `html-lore-v2` 即可回到只使用 1.x。不要用 2.0 写过的拷贝覆盖回 1.x，除非你明确接受 2.0 的编辑结果。现场回滚优先从 `/opt/backups/html-lore-v2-upgrade-<tag>-<ts>/` 还原 data / `.env` / compose。
