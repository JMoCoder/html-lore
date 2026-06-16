# HTMlore 部署安全基线

语言：[English](DEPLOYMENT.md) | [中文](DEPLOYMENT.zh-CN.md)

本文件定义项目层面可复用的部署与安全措施。它不是主机系统加固清单；每台自托管机器仍需要常规 OS、防火墙、SSH 或本地访问控制、公网部署时的 TLS，以及备份加固。

## 环境角色

- `main`：稳定生产分支。
- `develop`：日常开发与测试分支。
- 本机：开发环境与本地笔记本测试环境。
- 自托管 Docker 主机：可以是本地电脑、NAS、局域网服务器或 VPS，用于运行长期笔记本服务。本地电脑部署不要求 24 小时在线，除非你需要持续远程访问。
- `data/`：私有笔记本数据，不提交到 Git。

## 最低生产安全要求

不要在没有认证边界的情况下，把后端 API 直接暴露到公网。

项目层面必需控制：

- 后端设置 `HTML_LORE_API_TOKEN`。
- 公网访问前必须替换默认本地/测试账号 `admin` / `test-password`，并设置 `HTML_LORE_AUTH_USERNAME`、`HTML_LORE_AUTH_PASSWORD` 和 `HTML_LORE_SESSION_SECRET`。
- HTTPS 部署时设置 `HTML_LORE_SESSION_SECURE=true`。
- 设置 `HTML_LORE_CORS_ORIGINS` 为准确的前端公网来源。
- 静态前端和 API 都放在 HTTPS 后面。
- `data/content`、`data/meta` 和备份目录放在 Git 仓库之外。
- API Key 和后续模型凭据只保存在服务端。
- 用 `HTML_LORE_MAX_UPLOAD_BYTES` 限制上传大小。
- 部署前、结构性升级前备份 `data/`。

## 后端环境变量

```bash
HTML_LORE_CONTENT=/srv/html-lore/data/content
HTML_LORE_META=/srv/html-lore/data/meta
HTML_LORE_PUBLIC=/srv/html-lore/public
HTML_LORE_TITLE="HTMlore"
HTML_LORE_MAX_UPLOAD_BYTES=10485760
HTML_LORE_API_TOKEN="replace-with-a-long-random-token"
HTML_LORE_AUTH_USERNAME="admin"
HTML_LORE_AUTH_PASSWORD="replace-with-a-strong-login-password"
HTML_LORE_SESSION_SECRET="replace-with-a-long-random-session-secret"
HTML_LORE_SESSION_SECURE=true
HTML_LORE_CORS_ORIGINS="https://lore.example.com"
```

默认 Docker compose 会在应用容器内使用 `/data/content`、`/data/meta` 和 `/public`。如果不修改 compose 文件，宿主机路径就是仓库目录下的 `./data/...` 与 `./public`。

默认 `docker-compose.yml` 已启用内置登录，账号为 `admin` / `test-password`，并使用开发 session secret，便于本地测试开箱即用。任何公网部署前都必须在 `.env` 中替换这些值。
`.env.example` 只作为本地/私有网络模板；公网部署应以 `.env.secure.example` 为起点，并在启动服务前替换其中所有占位密钥。

后端只监听 localhost 或私有网络地址：

```bash
html-lore serve-api --host 127.0.0.1 --port 8787
```

## 前端 Token

本地测试可以让前端读取：

```html
<script>
  window.HTML_LORE_AGENT_URL = "https://lore.example.com";
  window.HTML_LORE_AGENT_TOKEN = "replace-with-a-long-random-token";
</script>
```

前端也会读取 `localStorage.html-lore-agent-token`，方便开发调试。生产环境优先使用内置浏览器登录，或使用反向代理登录/session 边界，不建议把长期 token 直接写进前端 HTML。为了兼容 iframe/raw HTML 访问，项目支持 query token，但它不应作为公网唯一安全边界。

## 反向代理边界

推荐生产布局：

```text
Browser
  -> HTTPS 反向代理
    -> HTMlore 内置登录/session
      -> static public/ frontend
      -> /api/*
```

反向代理应当：

- 终止 TLS；
- 使用 HTMlore 内置登录，或在访问应用前要求登录；
- 只转发明确需要的路径；
- 设置上传 body 大小限制；
- 不记录 Authorization header 或 query token。

默认 Docker 部署由单个应用容器同时提供前端和 `/api/*`。公网部署时，应把该容器放到你偏好的 HTTPS/认证边界之后。

可选的 `deploy/caddy-basic-auth.Caddyfile` 提供一种公网部署示例：

```text
Browser -> Caddy :80 with Basic Auth -> public/ 静态文件
Browser -> Caddy :80 with Basic Auth -> /api/* -> api:8787
```

Caddy 会先要求用户登录，再只在反代到内部 API 服务时注入 `Authorization: Bearer {$HTML_LORE_API_TOKEN}`。浏览器不需要保存，也不会看到长期后端 token。

## 自托管 Docker 部署

新主机上执行：

```bash
git clone https://github.com/JMoCoder/html_lore.git /srv/html-lore
cd /srv/html-lore
git checkout main
docker compose up -d --build
```

启动后检查容器健康状态：

```bash
docker compose ps
```

打开 `http://localhost:8080` 或 `http://你的主机-ip:8080`。

首次启动会自动创建 `data/content`、`data/meta` 和 `public` 绑定目录。上传的 HTML 保存到 `data/content`，元数据保存到 `data/meta`，重建后的静态资产保存到 `public`。

公网部署时，不要在没有认证边界的情况下暴露默认 compose。你可以使用自己的反向代理，也可以使用可选 Caddy Basic Auth 示例：

```bash
cp .env.secure.example .env
python3 - <<'PY'
import secrets
print("HTML_LORE_API_TOKEN=" + secrets.token_urlsafe(32))
PY
docker run --rm caddy:2-alpine caddy hash-password --plaintext 'change-this-login-password'
```

编辑 `.env`，填入生成的 token 和 Caddy 密码 hash，并将 `HTML_LORE_CORS_ORIGINS` 设置为你的公网来源。Caddy 密码 hash 包含 `$`。写入 `.env` 时必须把每个 `$` 转义为 `$$`。例如 `$2a$14$...` 应粘贴为 `$$2a$$14$$...`。

然后运行：

```bash
docker compose -f compose.prod.yml up -d --build
```

## 生产更新

HTMlore 不会自动更新宿主机。`GET /api/version` 和前端“关于项目”只显示更新提示。

手动更新流程：

```bash
cd /srv/html-lore
git fetch origin
git checkout main
git pull --ff-only
tar -czf "../html-lore-data-$(date +%Y%m%d-%H%M%S).tgz" data
docker compose up -d --build
docker compose logs -f
```

如果某个版本有数据迁移说明，运行新容器前必须备份 `data/`。回滚时切回旧 tag 或旧 commit 并重启 compose；如果版本改变了数据结构，还要恢复对应的 `data/` 备份。

## 部署流程

1. 在 `develop` 开发和测试。
2. 本地跑完整测试。
3. 将 `develop` 合并到 `main` 作为生产发布。
4. 自托管 Docker 主机拉取 `main`。
5. 备份 `/srv/html-lore/data`。
6. 通过 `docker compose up -d --build` 重建/重启容器。
7. 验证登录、上传、搜索、阅读、归档、版本显示和备份。

## 数据策略

`data/` 是私有运行时数据。它应该备份，不应推送到 GitHub。

推荐生产数据路径：

```text
/srv/html-lore/data/content
/srv/html-lore/data/meta
/srv/html-lore/backups
```

Git 只保存应用代码、测试和文档。
