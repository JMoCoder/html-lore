# HTMlore Deployment Baseline

Languages: [English](DEPLOYMENT.md) | [中文](DEPLOYMENT.zh-CN.md)

This document defines reusable project-level deployment and security measures.
It is not a host hardening checklist; each self-hosted machine still needs
normal OS, firewall, SSH or local access, TLS when public, and backup
hardening.

## Environment Roles

- `main`: stable production branch.
- `develop`: active development and test branch.
- Local workstation: development and local notebook testing.
- Self-hosted Docker host: local computer, NAS, LAN server, or VPS running the
  long-lived notebook service. A local computer deployment does not need to be
  online 24/7 unless you want continuous remote access.
- `data/`: private notebook data, not committed to Git.

## Minimal Production Security

Do not expose the backend API directly to the public internet without an
authentication boundary.

Required project-level controls:

- Set `HTML_LORE_API_TOKEN` for the backend API.
- Replace the default local/test login `admin` / `test-password` before public
  access by setting `HTML_LORE_AUTH_USERNAME`,
  `HTML_LORE_AUTH_PASSWORD`, and `HTML_LORE_SESSION_SECRET`.
- Set `HTML_LORE_SESSION_SECURE=true` when served over HTTPS.
- Set `HTML_LORE_CORS_ORIGINS` to the exact public frontend origin.
- Put the static frontend and API behind HTTPS.
- Keep `data/content`, `data/meta`, and backups outside the Git repository.
- Keep API keys and future model credentials on the server only.
- Limit upload size with `HTML_LORE_MAX_UPLOAD_BYTES`.
- Back up `data/` before deploys and before schema-changing upgrades.

## Backend Environment

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

The default Docker compose mounts those paths inside the app container as
`/data/content`, `/data/meta`, and `/public`; host-side directories remain
`./data/...` and `./public` relative to the checked-out repository unless you
change the compose file.

The default `docker-compose.yml` enables built-in login with
`admin` / `test-password` and a development session secret so local tests work
immediately. Change those values in `.env` before any public deployment.
Use `.env.example` as a local/private-network template. Use
`.env.secure.example` as the starting point for public deployments and replace
every placeholder secret before starting the service.

Run the backend only on localhost or a private network address:

```bash
html-lore serve-api --host 127.0.0.1 --port 8787
```

## Frontend Token

For local testing, the frontend can read:

```html
<script>
  window.HTML_LORE_AGENT_URL = "https://lore.example.com";
  window.HTML_LORE_AGENT_TOKEN = "replace-with-a-long-random-token";
</script>
```

The frontend also reads `localStorage.html-lore-agent-token` for development.
For production, prefer the built-in browser login or a reverse-proxy
login/session boundary over exposing a long-lived token in frontend HTML.
Query-token support exists for iframe/raw HTML access compatibility and should
not be the only public security boundary.

## Reverse Proxy Boundary

Recommended production layout:

```text
Browser
  -> HTTPS reverse proxy
    -> HTMlore built-in login/session
      -> static public/ frontend
      -> /api/*
```

The reverse proxy should:

- terminate TLS;
- either rely on HTMlore built-in login or require login before serving the app;
- forward only intended paths;
- set upload body limits;
- avoid logging Authorization headers or query tokens.

The default Docker deployment serves both the frontend and `/api/*` from the
single app container. Public deployments should put that container behind your
preferred HTTPS/authentication boundary.

The optional `deploy/caddy-basic-auth.Caddyfile` implements one possible public
deployment shape:

```text
Browser -> Caddy :80 with Basic Auth -> public/ static files
Browser -> Caddy :80 with Basic Auth -> /api/* -> api:8787
```

Caddy asks users to log in before serving the app, then injects
`Authorization: Bearer {$HTML_LORE_API_TOKEN}` only when proxying to the
internal API service. The browser does not need to store or see the long-lived
backend token.

## Self-Hosted Docker Deployment

On a fresh host:

```bash
git clone https://github.com/JMoCoder/html_lore.git /srv/html-lore
cd /srv/html-lore
git checkout main
docker compose up -d --build
```

Check the container health after startup:

```bash
docker compose ps
```

Open `http://localhost:8080` or `http://your-host-ip:8080`.

The first start creates `data/content`, `data/meta`, and `public` bind-mounted
directories if they do not already exist. Uploaded HTML files are stored under
`data/content`, metadata under `data/meta`, and rebuilt static assets under
`public`.

For public internet deployment, do not expose the default compose stack without
an authentication boundary. You can use your own reverse proxy, or the optional
Caddy Basic Auth example:

```bash
cp .env.secure.example .env
python3 - <<'PY'
import secrets
print("HTML_LORE_API_TOKEN=" + secrets.token_urlsafe(32))
PY
docker run --rm caddy:2-alpine caddy hash-password --plaintext 'change-this-login-password'
```

Edit `.env`, paste the generated token, paste the Caddy password hash, and set
`HTML_LORE_CORS_ORIGINS` to your public origin. Caddy password hashes contain
`$`; in `.env`, escape every `$` as `$$`. For example, `$2a$14$...` must be
pasted as `$$2a$$14$$...`.

Then run:

```bash
docker compose up -d --build
```

## Production Updates

HTMlore does not auto-update the host. `GET /api/version` and the frontend
About page only show update hints.

Manual update flow:

```bash
cd /srv/html-lore
git fetch origin
git checkout main
git pull --ff-only
tar -czf "../html-lore-data-$(date +%Y%m%d-%H%M%S).tgz" data
docker compose up -d --build
docker compose logs -f
```

If a release has a data migration note, back up `data/` before running the new
containers. Rollback means checking out the previous Git tag or commit and
restarting the compose stack; restore the matching `data/` backup if the release
changed data structure.

## Deployment Flow

1. Develop and test on `develop`.
2. Run full tests locally.
3. Merge `develop` into `main` for production release.
4. Pull `main` on the self-hosted Docker host.
5. Back up `/srv/html-lore/data`.
6. Rebuild/recreate containers with `docker compose up -d --build`.
7. Verify login, upload, search, read, archive, version display, and backup.

## Data Policy

`data/` is private runtime state. It should be backed up, not pushed to GitHub.
Recommended production data paths:

```text
/srv/html-lore/data/content
/srv/html-lore/data/meta
/srv/html-lore/backups
```

Git stores application code, tests, and docs only.
