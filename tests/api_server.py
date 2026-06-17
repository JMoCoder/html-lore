from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class ApiServer:
    def __init__(
        self,
        *,
        content_dir: Path,
        meta_dir: Path,
        public_dir: Path,
        site_title: str = "Test Vault",
        api_token: str = "",
        auth_username: str = "",
        auth_password: str = "",
        users_file: Path | None = None,
        user_data_dir: Path | None = None,
        session_secret: str = "",
        ai_provider: str = "",
        ai_base_url: str = "",
        ai_api_key: str = "",
        ai_model: str = "",
        ai_embedding_model: str = "",
        ai_enabled: bool = False,
        ai_external_search: str = "",
        ai_external_search_api_key: str = "",
        ai_external_search_max_results: int | None = None,
        ai_external_search_depth: str | None = None,
        ai_external_search_auto_parameters: bool | None = None,
        ai_external_search_topic: str | None = None,
        ai_external_search_time_range: str | None = None,
        ai_external_search_include_raw_content: bool | None = None,
        ai_max_context_items: int | None = None,
        ai_max_prompt_chars: int | None = None,
        ai_max_message_chars: int | None = None,
        ai_max_response_tokens: int | None = None,
        ai_rate_limit_requests: int | None = None,
        ai_rate_limit_window_seconds: int | None = None,
        ai_retrieval_mode: str | None = None,
        ai_qa_engine: str | None = None,
    ) -> None:
        self.port = free_port()
        self.api_token = api_token
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        env = os.environ.copy()
        env.update(
            {
                "HTML_LORE_CONTENT": str(content_dir),
                "HTML_LORE_META": str(meta_dir),
                "HTML_LORE_PUBLIC": str(public_dir),
                "HTML_LORE_TITLE": site_title,
                "HTML_LORE_API_TOKEN": api_token,
                "HTML_LORE_AUTH_USERNAME": auth_username,
                "HTML_LORE_AUTH_PASSWORD": auth_password,
                "HTML_LORE_SESSION_SECRET": session_secret,
                "HTML_LORE_AI_PROVIDER": ai_provider,
                "HTML_LORE_AI_BASE_URL": ai_base_url,
                "HTML_LORE_AI_API_KEY": ai_api_key,
                "HTML_LORE_AI_MODEL": ai_model,
                "HTML_LORE_AI_EMBEDDING_MODEL": ai_embedding_model,
                "HTML_LORE_AI_ENABLED": "true" if ai_enabled else "",
                "HTML_LORE_AI_EXTERNAL_SEARCH": ai_external_search,
                "HTML_LORE_AI_EXTERNAL_SEARCH_API_KEY": ai_external_search_api_key,
            },
        )
        if ai_max_context_items is not None:
            env["HTML_LORE_AI_MAX_CONTEXT_ITEMS"] = str(ai_max_context_items)
        if ai_external_search_max_results is not None:
            env["HTML_LORE_AI_EXTERNAL_SEARCH_MAX_RESULTS"] = str(ai_external_search_max_results)
        if ai_external_search_depth is not None:
            env["HTML_LORE_AI_EXTERNAL_SEARCH_DEPTH"] = ai_external_search_depth
        if ai_external_search_auto_parameters is not None:
            env["HTML_LORE_AI_EXTERNAL_SEARCH_AUTO_PARAMETERS"] = "true" if ai_external_search_auto_parameters else "false"
        if ai_external_search_topic is not None:
            env["HTML_LORE_AI_EXTERNAL_SEARCH_TOPIC"] = ai_external_search_topic
        if ai_external_search_time_range is not None:
            env["HTML_LORE_AI_EXTERNAL_SEARCH_TIME_RANGE"] = ai_external_search_time_range
        if ai_external_search_include_raw_content is not None:
            env["HTML_LORE_AI_EXTERNAL_SEARCH_INCLUDE_RAW_CONTENT"] = "true" if ai_external_search_include_raw_content else "false"
        if ai_max_prompt_chars is not None:
            env["HTML_LORE_AI_MAX_PROMPT_CHARS"] = str(ai_max_prompt_chars)
        if ai_max_message_chars is not None:
            env["HTML_LORE_AI_MAX_MESSAGE_CHARS"] = str(ai_max_message_chars)
        if ai_max_response_tokens is not None:
            env["HTML_LORE_AI_MAX_RESPONSE_TOKENS"] = str(ai_max_response_tokens)
        if ai_rate_limit_requests is not None:
            env["HTML_LORE_AI_RATE_LIMIT_REQUESTS"] = str(ai_rate_limit_requests)
        if ai_rate_limit_window_seconds is not None:
            env["HTML_LORE_AI_RATE_LIMIT_WINDOW_SECONDS"] = str(ai_rate_limit_window_seconds)
        if ai_retrieval_mode is not None:
            env["HTML_LORE_AI_RETRIEVAL_MODE"] = ai_retrieval_mode
        if ai_qa_engine is not None:
            env["HTML_LORE_AI_QA_ENGINE"] = ai_qa_engine
        if users_file:
            env["HTML_LORE_USERS_FILE"] = str(users_file)
        if user_data_dir:
            env["HTML_LORE_USER_DATA_DIR"] = str(user_data_dir)
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "html_lore.server.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
                "--log-level",
                "warning",
            ],
            cwd=Path(__file__).resolve().parents[1],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.wait_until_ready()

    def close(self) -> None:
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    def wait_until_ready(self) -> None:
        deadline = time.time() + 10
        while time.time() < deadline:
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                raise RuntimeError(f"API server exited early.\nstdout:\n{stdout}\nstderr:\n{stderr}")
            try:
                response = self.request("GET", "/api/health")
                if response["status"] == "ok":
                    return
            except (urllib.error.URLError, json.JSONDecodeError):
                time.sleep(0.1)
        raise RuntimeError("Timed out waiting for API server.")

    def request(self, method: str, path: str, *, query: dict[str, str] | None = None, body: bytes | None = None, headers: dict[str, str] | None = None) -> Any:
        return json.loads(self.request_text(method, path, query=query, body=body, headers=headers))

    def json(self, method: str, path: str, data: Any) -> Any:
        body = json.dumps(data).encode("utf-8")
        return self.request(
            method,
            path,
            body=body,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
            },
        )

    def json_error(self, method: str, path: str, data: Any) -> tuple[int, Any]:
        body = json.dumps(data).encode("utf-8")
        try:
            self.request(
                method,
                path,
                body=body,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body)),
                },
            )
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))
        raise AssertionError("Expected HTTP error response.")

    def request_text(self, method: str, path: str, *, query: dict[str, str] | None = None, body: bytes | None = None, headers: dict[str, str] | None = None) -> str:
        url = f"http://127.0.0.1:{self.port}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"
        request_headers = dict(headers or {})
        if self.api_token and "Authorization" not in request_headers:
            request_headers["Authorization"] = f"Bearer {self.api_token}"
        request = urllib.request.Request(url, data=body, method=method, headers=request_headers)
        with self.opener.open(request, timeout=5) as response:
            return response.read().decode("utf-8")

    def multipart(self, path: str, *, fields: dict[str, str], file_field: str, filename: str, content: bytes, content_type: str) -> Any:
        return json.loads(self.multipart_text(path, fields=fields, file_field=file_field, filename=filename, content=content, content_type=content_type))

    def multipart_error(self, path: str, *, fields: dict[str, str], file_field: str, filename: str, content: bytes, content_type: str) -> tuple[int, Any]:
        try:
            self.multipart_text(path, fields=fields, file_field=file_field, filename=filename, content=content, content_type=content_type)
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))
        raise AssertionError("Expected HTTP error response.")

    def multipart_text(self, path: str, *, fields: dict[str, str], file_field: str, filename: str, content: bytes, content_type: str) -> str:
        boundary = "----html-lore-test-boundary"
        chunks: list[bytes] = []
        for name, value in fields.items():
            chunks.extend(
                [
                    f"--{boundary}\r\n".encode("utf-8"),
                    f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                    value.encode("utf-8"),
                    b"\r\n",
                ],
            )
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
                content,
                b"\r\n",
                f"--{boundary}--\r\n".encode("utf-8"),
            ],
        )
        body = b"".join(chunks)
        return self.request_text(
            "POST",
            path,
            body=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Content-Length": str(len(body)),
            },
        )


def run_api_server(
    *,
    content_dir: Path,
    meta_dir: Path,
    public_dir: Path,
    site_title: str = "Test Vault",
    api_token: str = "",
    auth_username: str = "",
    auth_password: str = "",
    users_file: Path | None = None,
    user_data_dir: Path | None = None,
    session_secret: str = "",
    ai_provider: str = "",
    ai_base_url: str = "",
    ai_api_key: str = "",
    ai_model: str = "",
    ai_embedding_model: str = "",
    ai_enabled: bool = False,
    ai_external_search: str = "",
    ai_external_search_api_key: str = "",
    ai_external_search_max_results: int | None = None,
    ai_external_search_depth: str | None = None,
    ai_external_search_auto_parameters: bool | None = None,
    ai_external_search_topic: str | None = None,
    ai_external_search_time_range: str | None = None,
    ai_external_search_include_raw_content: bool | None = None,
    ai_max_context_items: int | None = None,
    ai_max_prompt_chars: int | None = None,
    ai_max_message_chars: int | None = None,
    ai_max_response_tokens: int | None = None,
    ai_rate_limit_requests: int | None = None,
    ai_rate_limit_window_seconds: int | None = None,
    ai_retrieval_mode: str | None = None,
    ai_qa_engine: str | None = None,
) -> ApiServer:
    return ApiServer(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title=site_title,
        api_token=api_token,
        auth_username=auth_username,
        auth_password=auth_password,
        users_file=users_file,
        user_data_dir=user_data_dir,
        session_secret=session_secret,
        ai_provider=ai_provider,
        ai_base_url=ai_base_url,
        ai_api_key=ai_api_key,
        ai_model=ai_model,
        ai_embedding_model=ai_embedding_model,
        ai_enabled=ai_enabled,
        ai_external_search=ai_external_search,
        ai_external_search_api_key=ai_external_search_api_key,
        ai_external_search_max_results=ai_external_search_max_results,
        ai_external_search_depth=ai_external_search_depth,
        ai_external_search_auto_parameters=ai_external_search_auto_parameters,
        ai_external_search_topic=ai_external_search_topic,
        ai_external_search_time_range=ai_external_search_time_range,
        ai_external_search_include_raw_content=ai_external_search_include_raw_content,
        ai_max_context_items=ai_max_context_items,
        ai_max_prompt_chars=ai_max_prompt_chars,
        ai_max_message_chars=ai_max_message_chars,
        ai_max_response_tokens=ai_max_response_tokens,
        ai_rate_limit_requests=ai_rate_limit_requests,
        ai_rate_limit_window_seconds=ai_rate_limit_window_seconds,
        ai_retrieval_mode=ai_retrieval_mode,
        ai_qa_engine=ai_qa_engine,
    )
