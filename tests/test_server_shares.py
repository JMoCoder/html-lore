import html
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

from html_lore.server.shares import scan_share_content
from tests.api_server import run_api_server


ROOT = Path(__file__).resolve().parents[1]


def test_share_safety_does_not_treat_risk_table_css_class_as_secret() -> None:
    scan = scan_share_content('<html><body><table class="risk-table-mobile"><tr><td>Risk</td></tr></table></body></html>')
    assert scan["shareable"] is True


def copy_fixture_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    content_dir = tmp_path / "content"
    meta_dir = tmp_path / "meta"
    public_dir = tmp_path / "public"
    shutil.copytree(ROOT / "examples" / "content", content_dir)
    shutil.copytree(ROOT / "examples" / "meta", meta_dir)
    return content_dir, meta_dir, public_dir


def test_share_link_allows_public_sanitized_note_without_login(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Share Test",
        auth_username="admin",
        auth_password="correct-password",
        session_secret="test-session-secret",
    )
    try:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{server.port}/api/items/imported/docker-network.html/raw", timeout=5)
        except urllib.error.HTTPError as exc:
            assert exc.code == 401
        else:
            raise AssertionError("Expected raw item access to require login.")

        server.json("POST", "/api/auth/login", {"username": "admin", "password": "correct-password"})
        created = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1d"})

        assert created["share"]["active"] is True
        assert created["share"]["url_path"] == created["url_path"]
        assert created["url_path"].startswith("/share/")
        assert created["token"]

        public_json = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}/api/public/shares/{created['token']}",
            timeout=5,
        ).read().decode("utf-8")
        public_page = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}",
            timeout=5,
        ).read().decode("utf-8")
        public_page_trailing_slash = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}/",
            timeout=5,
        ).read().decode("utf-8")

        assert "Docker Network Quick Notes" in public_json
        assert "Docker Network Quick Notes" in public_page
        assert "imported/docker-network.html" not in public_json
        assert "\"id\"" not in public_json
        assert "\"collection\"" not in public_json
        assert "\"tags\"" not in public_json
        assert "\"url_path\"" not in public_json
        assert "ai_provider" not in public_json.lower()
        assert "api_key" not in public_json.lower()
        assert "token_hash" not in public_json.lower()
        assert "run" not in public_json.lower()
        assert "HTMlore shared note" in public_page
        assert "HTMlore shared note" in public_page_trailing_slash
        assert "Download shared HTML" in public_page
        assert "share-download-button" in public_page
        assert "GitHub repository" not in public_page_trailing_slash
        assert public_page.count("<html") == 1
        assert public_page.count("<head") == 1
        assert public_page.count("<body") == 1
        assert "<iframe" in public_page
        assert "srcdoc=" in public_page
        assert "width: 100%; min-height: 70vh; margin: 0;" in public_page
        assert "width: min(1100px, 100%)" not in public_page

        shares = server.request("GET", "/api/shares")
        assert shares["shares"][0]["url_path"] == created["url_path"]
        static_shell = public_dir / "share" / created["token"] / "index.html"
        assert static_shell.exists()
        assert '<base href="/">' in static_shell.read_text(encoding="utf-8")
    finally:
        server.close()


def test_public_share_token_does_not_grant_private_api_access(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Share Test",
        auth_username="admin",
        auth_password="correct-password",
        session_secret="test-session-secret",
    )
    try:
        server.json("POST", "/api/auth/login", {"username": "admin", "password": "correct-password"})
        created = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1d"})
        server.cookie_jar.clear()

        public_json = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}/api/public/shares/{created['token']}",
            timeout=5,
        ).read().decode("utf-8")
        assert "Docker Network Quick Notes" in public_json

        for private_path in [
            "/api/manifest",
            "/api/shares",
            "/api/ai/status",
            "/api/ai/runs",
            "/api/ai/conversations",
            "/api/items/imported/docker-network.html/raw",
            f"/api/items/imported/docker-network.html/raw?access_token={created['token']}",
            f"/api/ai/status?access_token={created['token']}",
        ]:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{server.port}{private_path}", timeout=5)
            except urllib.error.HTTPError as exc:
                assert exc.code == 401
            else:
                raise AssertionError(f"Expected private API path to require login: {private_path}")
    finally:
        server.close()


def test_share_list_keeps_copyable_url_after_update(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1d"})
        updated = server.json("PATCH", f"/api/shares/{created['share']['id']}", {"duration": "7d"})
        shares = server.request("GET", "/api/shares")

        assert updated["url_path"] == created["url_path"]
        assert shares["shares"][0]["url_path"] == created["url_path"]
    finally:
        server.close()


def test_public_share_read_repairs_existing_static_shell(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1d"})
        static_shell = public_dir / "share" / created["token"] / "index.html"
        static_shell.write_text("<!doctype html><html><head></head><body>broken shell</body></html>", encoding="utf-8")

        urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}/api/public/shares/{created['token']}",
            timeout=5,
        ).read()

        repaired = static_shell.read_text(encoding="utf-8")
        assert '<base href="/">' in repaired
        assert "broken shell" not in repaired
    finally:
        server.close()


def test_revoked_share_cannot_be_reactivated_or_updated(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1d"})
        server.request("DELETE", f"/api/shares/{created['share']['id']}")

        status, error = server.json_error("PATCH", f"/api/shares/{created['share']['id']}", {"revoked": False})
        assert status == 400
        assert "reactivated" in error["detail"]

        status, error = server.json_error("PATCH", f"/api/shares/{created['share']['id']}", {"duration": "7d"})
        assert status == 400
        assert "Inactive" in error["detail"]
    finally:
        server.close()


def test_expired_share_cannot_be_updated(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1h"})
        store = meta_dir / "config" / "shares.json"
        data = json.loads(store.read_text(encoding="utf-8"))
        data["shares"][0]["expires_at"] = "2000-01-01T00:00:00+00:00"
        store.write_text(json.dumps(data), encoding="utf-8")

        status, error = server.json_error("PATCH", f"/api/shares/{created['share']['id']}", {"duration": "7d"})
        assert status == 400
        assert "Inactive" in error["detail"]
    finally:
        server.close()


def test_shared_page_isolates_source_global_styles(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    styled = content_dir / "imported" / "global-style.html"
    styled.parent.mkdir(parents=True, exist_ok=True)
    styled.write_text(
        """<html>
<head>
  <title>Global Style</title>
  <style>
    body { display: grid; place-items: center; min-height: 100vh; }
    svg { width: 900px; height: 900px; }
  </style>
</head>
<body>
  <h1>Real shared content</h1>
  <svg viewBox="0 0 100 100"><path d="M50 5 L95 95 H5 Z"></path></svg>
</body>
</html>""",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/global-style.html", "duration": "1d"})
        public_page = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}",
            timeout=5,
        ).read().decode("utf-8")

        assert "Real shared content" in public_page
        assert ".share-shell" in public_page
        assert "srcdoc=" in public_page
        assert "body { display: grid; place-items: center; min-height: 100vh; }" in public_page
        assert public_page.find("body { display: grid") > public_page.find("srcdoc=")
    finally:
        server.close()


def test_safe_share_creation_creates_static_copy_for_scripted_html(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    unsafe = content_dir / "imported" / "unsafe.html"
    unsafe.parent.mkdir(parents=True, exist_ok=True)
    unsafe.write_text(
        "<html><head><title>Unsafe</title></head><body><script>alert(1)</script><a href=\"https://example.com\">out</a></body></html>",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/unsafe.html", "duration": "1d"})
        share = created["share"]
        copied_path = content_dir / share["content_item_id"]
        public = urllib.request.urlopen(f"http://127.0.0.1:{server.port}{created['url_path']}", timeout=5).read().decode("utf-8")

        assert share["mode"] == "safe"
        assert share["item_id"] == "imported/unsafe.html"
        assert share["content_item_id"].startswith("imported/unsafe--safe-share")
        assert share["repair"]["engine"] == "deterministic"
        assert copied_path.exists()
        assert "<script" not in copied_path.read_text(encoding="utf-8")
        assert "<script>alert(1)</script>" in unsafe.read_text(encoding="utf-8")
        assert "alert(1)" not in public
    finally:
        server.close()


def test_share_allows_safe_toggle_interaction_without_source_script(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    collapsible = content_dir / "imported" / "collapsible.html"
    collapsible.parent.mkdir(parents=True, exist_ok=True)
    collapsible.write_text(
        """<html>
<head>
  <title>Collapsible</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap" rel="stylesheet">
</head>
<body>
  <div class="qgroup-header" onclick="toggleGroup('g1')">Open group</div>
  <div class="qgroup open" id="g1">Group body</div>
  <script>
    function toggleGroup(id) {
      const el = document.getElementById(id);
      el.classList.toggle('open');
    }

    // Open first group by default (already set via class)
    // Add keyboard shortcut: press '?' to expand all
    document.addEventListener('keydown', e => {
      if (e.key === '?') {
        document.querySelectorAll('.qgroup').forEach(g => g.classList.add('open'));
      }
      if (e.key === '/') {
        document.querySelectorAll('.qgroup').forEach(g => g.classList.remove('open'));
        document.getElementById('g1').classList.add('open');
      }
    });
  </script>
</body>
</html>""",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/collapsible.html", "duration": "1d"})
        public_page = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}",
            timeout=5,
        ).read().decode("utf-8")
        srcdoc = html.unescape(public_page)

        assert created["share"]["active"] is True
        assert 'data-share-toggle="g1"' in srcdoc
        assert "onclick=" not in srcdoc
        assert "fonts.googleapis.com" not in srcdoc
        assert "function toggleGroup" not in srcdoc
    finally:
        server.close()


def test_share_still_blocks_unsafe_inline_handlers(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    unsafe = content_dir / "imported" / "unsafe-handler.html"
    unsafe.parent.mkdir(parents=True, exist_ok=True)
    unsafe.write_text("<html><body><div onclick=\"fetch('/api/items')\">bad</div></body></html>", encoding="utf-8")
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/unsafe-handler.html", "duration": "1d"})
        copied = (content_dir / created["share"]["content_item_id"]).read_text(encoding="utf-8")

        assert created["share"]["repair"]["created"] is True
        assert "onclick=" not in copied
        assert "fetch('/api/items')" not in copied
    finally:
        server.close()


def test_interactive_share_preserves_trusted_html_inside_isolated_frame(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    interactive = content_dir / "imported" / "interactive.html"
    interactive.parent.mkdir(parents=True, exist_ok=True)
    interactive.write_text(
        """<!doctype html><html><head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">
</head><body><canvas id="chart"></canvas><button onclick="draw()">Draw</button>
<script>function draw() { new Chart(document.getElementById('chart'), {}); }</script>
</body></html>""",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json(
            "POST",
            "/api/shares",
            {"item_id": "imported/interactive.html", "duration": "1d", "mode": "interactive"},
        )
        public_data = server.request("GET", f"/api/public/shares/{created['token']}")
        public_page = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}", timeout=5,
        ).read().decode("utf-8")

        assert created["share"]["mode"] == "interactive"
        assert public_data["share"]["mode"] == "interactive"
        assert "cdn.jsdelivr.net/npm/chart.js" in public_data["html"]
        assert "onclick=\"draw()\"" in public_data["html"]
        assert "sandbox=\"allow-scripts\"" in public_page
        assert "allow-same-origin" not in public_page
        assert "allow-forms" not in public_page
        assert "allow-popups" not in public_page
    finally:
        server.close()


def test_interactive_share_requires_confirmation_for_private_reference(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    interactive = content_dir / "imported" / "internal-dashboard.html"
    interactive.parent.mkdir(parents=True, exist_ok=True)
    interactive.write_text(
        '<html><body><script src="http://192.168.1.12/chart.js"></script><div>Dashboard</div></body></html>',
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        status, error = server.json_error(
            "POST",
            "/api/shares",
            {"item_id": "imported/internal-dashboard.html", "duration": "1d", "mode": "interactive"},
        )
        assert status == 409
        assert error["detail"]["requires_confirmation"] is True
        assert "private-local-reference" in error["detail"]["safety"]["warnings"]

        created = server.json(
            "POST",
            "/api/shares",
            {
                "item_id": "imported/internal-dashboard.html",
                "duration": "1d",
                "mode": "interactive",
                "confirm_private_references": True,
            },
        )
        assert created["share"]["active"] is True
    finally:
        server.close()


def test_interactive_share_still_blocks_secrets_and_navigation_escape_tags(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    unsafe = content_dir / "imported" / "secret.html"
    unsafe.parent.mkdir(parents=True, exist_ok=True)
    unsafe.write_text(
        '<html><head><base href="https://evil.example/"></head><body>api_key=super-secret-value<script>alert(1)</script></body></html>',
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        status, error = server.json_error(
            "POST",
            "/api/shares",
            {"item_id": "imported/secret.html", "duration": "1d", "mode": "interactive"},
        )
        assert status == 400
        assert "blocked-tag:base" in error["detail"]["safety"]["reasons"]
        assert "sensitive-secret" in error["detail"]["safety"]["reasons"]
    finally:
        server.close()


def test_shared_page_disables_external_links(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    linked = content_dir / "imported" / "linked.html"
    linked.parent.mkdir(parents=True, exist_ok=True)
    linked.write_text(
        "<html><head><title>Linked</title></head><body><h1>Linked</h1><a href=\"https://example.com\">external</a></body></html>",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/linked.html", "duration": "1d"})
        public_page = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}",
            timeout=5,
        ).read().decode("utf-8")

        assert "Linked" in public_page
        assert "external" in public_page
        assert "https://example.com" not in public_page
    finally:
        server.close()


def test_shared_page_drops_internal_and_external_resource_sources(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    linked = content_dir / "imported" / "resource-linked.html"
    linked.parent.mkdir(parents=True, exist_ok=True)
    linked.write_text(
        """<html><body>
<h1>Resources</h1>
<img src="/api/manifest" alt="api">
<img src="content/imported/docker-network.html" alt="content">
<img src="https://example.com/pixel.png" alt="external">
<img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='4' cy='4' r='4'/%3E%3C/svg%3E" alt="safe">
</body></html>""",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/resource-linked.html", "duration": "1d"})
        public_page = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}",
            timeout=5,
        ).read().decode("utf-8")
        srcdoc = html.unescape(public_page)

        assert "Resources" in srcdoc
        assert "/api/manifest" not in srcdoc
        assert "content/imported/docker-network.html" not in srcdoc
        assert "https://example.com/pixel.png" not in srcdoc
        assert "data:image/svg+xml" in srcdoc
    finally:
        server.close()


def test_shared_page_preserves_safe_styles_and_fragment_links(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    styled = content_dir / "imported" / "styled.html"
    styled.parent.mkdir(parents=True, exist_ok=True)
    styled.write_text(
        """<html>
<head>
  <title>Styled</title>
  <style>
    :root { --accent: #0f766e; }
    html { scroll-behavior: smooth; }
    body { color: #172033; }
    .card { border: 1px solid #d9e2ec; border-radius: 8px; }
    .hero { background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='4' cy='4' r='4'/%3E%3C/svg%3E"); }
  </style>
</head>
<body>
  <a href="#overview">overview</a>
  <a href="https://example.com">external</a>
  <section id="overview" class="card">Styled body</section>
</body>
</html>""",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/styled.html", "duration": "1d"})
        public_page = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}",
            timeout=5,
        ).read().decode("utf-8")
        srcdoc = html.unescape(public_page)

        assert "<style>" in srcdoc
        assert "border-radius: 8px" in srcdoc
        assert "scroll-behavior: smooth" in srcdoc
        assert "data:image/svg+xml" in srcdoc
        assert 'href="#overview"' in srcdoc
        assert "scrollToFragment" in srcdoc
        assert "event.preventDefault()" in srcdoc
        assert "https://example.com" not in srcdoc
        assert public_page.count("<html") == 1
        assert public_page.count("<head") == 1
        assert public_page.count("<body") == 1
    finally:
        server.close()


def test_safe_share_removes_unsafe_css_resources(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    unsafe = content_dir / "imported" / "unsafe-css.html"
    unsafe.parent.mkdir(parents=True, exist_ok=True)
    unsafe.write_text(
        "<html><head><style>@import url('https://example.com/a.css'); body{background:url(file:///tmp/x)} .x{behavior:url(#default#VML)}</style></head><body>bad</body></html>",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/unsafe-css.html", "duration": "1d"})
        copied = (content_dir / created["share"]["content_item_id"]).read_text(encoding="utf-8")

        assert created["share"]["repair"]["created"] is True
        assert "@import" not in copied
        assert "file:///tmp/x" not in copied
    finally:
        server.close()


def test_safe_share_replaces_chart_with_static_notice(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    chart = content_dir / "imported" / "chart.html"
    chart.parent.mkdir(parents=True, exist_ok=True)
    chart.write_text(
        """<html>
<head><script src="https://cdn.example.com/chart.umd.min.js"></script></head>
<body><canvas id="chart"></canvas><script>new Chart(document.getElementById('chart'), {});</script></body>
</html>""",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/chart.html", "duration": "1d"})
        copied = (content_dir / created["share"]["content_item_id"]).read_text(encoding="utf-8")

        assert created["share"]["repair"]["created"] is True
        assert "Interactive content was removed" in copied
        assert "<canvas" not in copied
    finally:
        server.close()


def test_shared_page_disables_internal_links(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    linked = content_dir / "imported" / "internal-linked.html"
    linked.parent.mkdir(parents=True, exist_ok=True)
    linked.write_text(
        "<html><body><a href=\"../generated/example.html\">internal</a></body></html>",
        encoding="utf-8",
    )
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/internal-linked.html", "duration": "1d"})
        public_page = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{created['url_path']}",
            timeout=5,
        ).read().decode("utf-8")

        assert "internal" in public_page
        assert "../generated/example.html" not in public_page
        assert "<a href=" not in public_page
    finally:
        server.close()


def test_replacing_share_revokes_previous_token(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        first = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1h"})
        first_shell = public_dir / "share" / first["token"] / "index.html"
        assert first_shell.exists()
        second = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1d"})
        second_shell = public_dir / "share" / second["token"] / "index.html"

        assert first["token"] != second["token"]
        assert not first_shell.exists()
        assert second_shell.exists()
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{server.port}/api/public/shares/{first['token']}", timeout=5)
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        else:
            raise AssertionError("Expected replaced share token to be revoked.")

        public_json = urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}/api/public/shares/{second['token']}",
            timeout=5,
        ).read().decode("utf-8")
        assert "Docker Network Quick Notes" in public_json
    finally:
        server.close()


def test_share_rechecks_safety_when_public_link_is_used(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    target = content_dir / "imported" / "docker-network.html"
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1d"})
        target.write_text("<html><body><script>alert(1)</script></body></html>", encoding="utf-8")

        try:
            urllib.request.urlopen(f"http://127.0.0.1:{server.port}/api/public/shares/{created['token']}", timeout=5)
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        else:
            raise AssertionError("Expected mutated unsafe share to be unavailable.")

        shares = server.request("GET", "/api/shares")
        assert shares["shares"][0]["active"] is False
        assert "blocked-tag:script" in shares["shares"][0]["safety"]["reasons"]
    finally:
        server.close()


def test_revoked_share_stops_public_access(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(content_dir=content_dir, meta_dir=meta_dir, public_dir=public_dir, site_title="Share Test")
    try:
        created = server.json("POST", "/api/shares", {"item_id": "imported/docker-network.html", "duration": "1h"})
        static_shell = public_dir / "share" / created["token"] / "index.html"
        assert static_shell.exists()
        revoked = server.request("DELETE", f"/api/shares/{created['share']['id']}")

        assert revoked["active"] is False
        assert not static_shell.exists()
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{server.port}/api/public/shares/{created['token']}", timeout=5)
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        else:
            raise AssertionError("Expected revoked share to be unavailable.")
    finally:
        server.close()
