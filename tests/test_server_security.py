import shutil
import urllib.error
import urllib.request
import json
from pathlib import Path

from html_lore.builder import build_site

from tests.api_server import run_api_server
from html_lore.server.config import ServerSettings
from html_lore.server.config import load_settings
from html_lore.server.users import UserStore


ROOT = Path(__file__).resolve().parents[1]


def copy_fixture_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    content_dir = tmp_path / "content"
    meta_dir = tmp_path / "meta"
    public_dir = tmp_path / "public"
    shutil.copytree(ROOT / "examples" / "content", content_dir)
    shutil.copytree(ROOT / "examples" / "meta", meta_dir)
    return content_dir, meta_dir, public_dir


def test_api_token_protects_manifest(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Security Test",
        api_token="secret-token",
    )
    try:
        url = f"http://127.0.0.1:{server.port}/api/manifest"
        try:
            urllib.request.urlopen(url, timeout=5)
        except urllib.error.HTTPError as exc:
            assert exc.code == 401
        else:
            raise AssertionError("Expected unauthenticated manifest request to fail.")

        manifest = server.request("GET", "/api/manifest")
        assert manifest["version"] == 2
    finally:
        server.close()


def test_api_token_query_allows_iframe_content(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    server = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Security Test",
        api_token="secret-token",
    )
    try:
        content = server.request_text(
            "GET",
            "/api/items/imported/docker-network.html/content",
            query={"access_token": "secret-token"},
            headers={"Authorization": ""},
        )
        assert "Docker Network Quick Notes" in content
    finally:
        server.close()


def test_api_server_serves_static_frontend(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    build_site(content_dir, meta_dir, public_dir, "Static Test")
    server = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Static Test",
    )
    try:
        index = server.request_text("GET", "/")
        assert "<title>HTMlore</title>" in index
        health = server.request("GET", "/api/health")
        assert health["status"] == "ok"
    finally:
        server.close()


def test_html_lore_env_names_configure_server(monkeypatch, tmp_path: Path) -> None:
    lore_content = tmp_path / "lore-content"
    monkeypatch.setenv("HTML_LORE_CONTENT", str(lore_content))
    monkeypatch.setenv("HTML_LORE_TITLE", "HTMlore Title")
    monkeypatch.setenv("HTML_LORE_SESSION_SECRET", "secret")
    monkeypatch.setenv("HTML_LORE_AI_QA_ENGINE", "langgraph")

    settings = load_settings()

    assert settings.content_dir == lore_content
    assert settings.site_title == "HTMlore Title"
    assert settings.session_secret == "secret"
    assert settings.ai_qa_engine == "langgraph"


def test_default_ai_qa_engine_is_auto(monkeypatch) -> None:
    monkeypatch.delenv("HTML_LORE_AI_QA_ENGINE", raising=False)

    settings = load_settings()

    assert settings.ai_qa_engine == "auto"


def test_unknown_env_prefixes_do_not_configure_server(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "unknown-content"
    monkeypatch.setenv("HTML_OTHER_CONTENT", str(content))
    monkeypatch.setenv("HTML_OTHER_TITLE", "Unknown Title")
    monkeypatch.setenv("HTML_OTHER_SESSION_SECRET", "unknown-secret")

    settings = load_settings()

    assert settings.content_dir == Path("content")
    assert settings.site_title == "HTMlore"
    assert settings.session_secret == ""


def test_login_session_protects_api_and_content(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    build_site(content_dir, meta_dir, public_dir, "Auth Test")
    server = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Auth Test",
        auth_username="admin",
        auth_password="correct-password",
        session_secret="test-session-secret",
    )
    try:
        status = server.request("GET", "/api/auth/status")
        assert status == {"enabled": True, "authenticated": False, "user": None, "data_id": None}

        for path in ["/api/manifest", "/manifest.json", "/content/imported/docker-network.html"]:
            try:
                server.request_text("GET", path)
            except urllib.error.HTTPError as exc:
                assert exc.code == 401
            else:
                raise AssertionError(f"Expected unauthenticated request to fail: {path}")

        body = json.dumps({"username": "admin", "password": "wrong-password"}).encode("utf-8")
        try:
            server.request_text(
                "POST",
                "/api/auth/login",
                body=body,
                headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
            )
        except urllib.error.HTTPError as exc:
            assert exc.code == 401
        else:
            raise AssertionError("Expected invalid login to fail.")

        body = json.dumps({"username": "ADMIN", "password": "correct-password"}).encode("utf-8")
        login = server.request(
            "POST",
            "/api/auth/login",
            body=body,
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        assert login == {"enabled": True, "authenticated": True, "user": "admin", "data_id": "default"}

        manifest = server.request("GET", "/api/manifest")
        assert manifest["version"] == 2
        static_manifest = server.request("GET", "/manifest.json")
        assert static_manifest["version"] == 2
        content = server.request_text("GET", "/content/imported/docker-network.html")
        assert "Docker Network Quick Notes" in content
    finally:
        server.close()


def test_login_bootstraps_users_file_from_env(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    users_file = tmp_path / "users.json"
    build_site(content_dir, meta_dir, public_dir, "Auth Test")
    server = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Auth Test",
        auth_username="admin",
        auth_password="correct-password",
        users_file=users_file,
        user_data_dir=tmp_path / "users",
        session_secret="test-session-secret",
    )
    try:
        assert users_file.exists()
        data = json.loads(users_file.read_text(encoding="utf-8"))
        assert data["users"][0]["username"] == "admin"
        assert data["users"][0]["data_id"] == "default"
        assert data["users"][0]["password_hash"].startswith("pbkdf2_sha256$")

        login = server.json("POST", "/api/auth/login", {"username": "ADMIN", "password": "correct-password"})
        assert login == {"enabled": True, "authenticated": True, "user": "admin", "data_id": "default"}
    finally:
        server.close()


def test_multi_user_uploads_are_persisted_in_separate_partitions(tmp_path: Path) -> None:
    content_dir, meta_dir, public_dir = copy_fixture_tree(tmp_path)
    users_file = tmp_path / "users.json"
    user_data_dir = tmp_path / "users"
    settings = ServerSettings(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Auth Test",
        max_upload_bytes=10 * 1024 * 1024,
        users_file=users_file,
    )
    store = UserStore(settings)
    store.add_user(username="alice", password="alice-password", data_id="alice")
    store.add_user(username="bob", password="bob-password", data_id="bob")

    build_site(content_dir, meta_dir, public_dir, "Auth Test")
    alice = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Auth Test",
        users_file=users_file,
        user_data_dir=user_data_dir,
        session_secret="test-session-secret",
    )
    bob = run_api_server(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title="Auth Test",
        users_file=users_file,
        user_data_dir=user_data_dir,
        session_secret="test-session-secret",
    )
    try:
        alice.json("POST", "/api/auth/login", {"username": "ALICE", "password": "alice-password"})
        bob.json("POST", "/api/auth/login", {"username": "bob", "password": "bob-password"})

        alice_upload = alice.multipart(
            "/api/uploads/html",
            fields={"title": "Alice Note", "summary": "", "collection": "Inbox", "tags": "private"},
            file_field="file",
            filename="alice-note.html",
            content=b"<html><head><title>Alice Private</title></head><body>Alice only</body></html>",
            content_type="text/html",
        )
        bob_manifest = bob.request("GET", "/api/manifest")
        alice_manifest = alice.request("GET", "/api/manifest")

        assert alice_upload["item_id"].startswith("imported/")
        assert [item["title"] for item in alice_manifest["items"]] == ["Alice Note"]
        assert bob_manifest["items"] == []
        assert (user_data_dir / "alice" / "content" / alice_upload["item_id"]).exists()
        assert not (user_data_dir / "bob" / "content" / alice_upload["item_id"]).exists()
    finally:
        alice.close()
        bob.close()
