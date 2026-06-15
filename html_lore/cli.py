from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from .builder import build_site
from .server.ai.eval import KnowledgeQAEvalSpec, load_eval_questions, run_knowledge_qa_eval
from .server.ai.providers import AIProviderConfigStore
from .server.ai.runtime_eval import QARuntimeEvalSpec, load_runtime_eval_cases, run_qa_runtime_eval
from .server.ai.vector_maintenance import VectorMaintenanceError, vector_maintenance_for_config
from .server.config import ServerSettings, load_settings
from .server.items import ItemService
from .server.users import UserStore, UserStoreError


def main(argv: Sequence[str] | None = None, *, prog: str = "html-lore") -> None:
    parser = argparse.ArgumentParser(prog=prog)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build the static HTMlore site.")
    build_parser.add_argument("--content", default="content", help="Directory containing source HTML files.")
    build_parser.add_argument("--meta", default="meta", help="Directory containing sidecar metadata.")
    build_parser.add_argument("--out", default="public", help="Output directory for the static site.")
    build_parser.add_argument("--title", default="HTMlore", help="Site title.")

    api_parser = subparsers.add_parser("serve-api", help="Run the optional backend API server.")
    api_parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    api_parser.add_argument("--port", type=int, default=8787, help="Port to bind.")

    user_parser = subparsers.add_parser("user-add", help="Add or update a self-hosted login user.")
    user_parser.add_argument("--users-file", default="data/users.json", help="Path to users.json.")
    user_parser.add_argument("--username", required=True, help="Login username. Matching is case-insensitive.")
    user_parser.add_argument("--password", required=True, help="Login password. Stored as a PBKDF2 hash.")
    user_parser.add_argument("--role", default="user", choices=["admin", "user"], help="User role.")
    user_parser.add_argument("--data-id", default="", help="Optional persistent data partition id.")
    user_parser.add_argument("--replace", action="store_true", help="Replace the user if it already exists.")

    qa_eval_parser = subparsers.add_parser("ai-eval-qa", help="Run a non-persistent knowledge QA evaluation baseline.")
    qa_eval_parser.add_argument("--content", default="examples/content", help="Directory containing source HTML files.")
    qa_eval_parser.add_argument("--meta", default="examples/meta", help="Directory containing sidecar metadata.")
    qa_eval_parser.add_argument("--public", default="examples/public", help="Public output directory used for settings.")
    qa_eval_parser.add_argument("--questions", default="", help="JSON file containing a list of evaluation questions.")
    qa_eval_parser.add_argument("--provider", default="fake", choices=["fake", "openai-compatible"], help="AI provider for evaluation.")
    qa_eval_parser.add_argument("--base-url", default="", help="OpenAI-compatible base URL when using a real provider.")
    qa_eval_parser.add_argument("--api-key-env", default="HTML_LORE_AI_API_KEY", help="Environment variable containing the real provider API key.")
    qa_eval_parser.add_argument("--model", default="fake-eval-model", help="Model name for evaluation.")
    qa_eval_parser.add_argument("--retrieval-mode", default="keyword", choices=["keyword", "vector", "hybrid"], help="Retrieval mode to evaluate.")
    qa_eval_parser.add_argument("--source-mode", default="local_only", choices=["local_only", "local_plus_external"], help="QA source mode.")
    qa_eval_parser.add_argument("--out", default="", help="Optional JSON output path. Defaults to stdout.")

    qa_runtime_eval_parser = subparsers.add_parser("ai-eval-qa-runtime", help="Compare legacy QA graph and the new AgentRuntime QA agent.")
    qa_runtime_eval_parser.add_argument("--content", default="examples/content", help="Directory containing source HTML files.")
    qa_runtime_eval_parser.add_argument("--meta", default="examples/meta", help="Directory containing sidecar metadata.")
    qa_runtime_eval_parser.add_argument("--public", default="examples/public", help="Public output directory used for settings.")
    qa_runtime_eval_parser.add_argument("--cases", default="", help="JSON file containing runtime evaluation cases.")
    qa_runtime_eval_parser.add_argument("--provider", default="fake", choices=["fake", "openai-compatible"], help="AI provider for evaluation.")
    qa_runtime_eval_parser.add_argument("--base-url", default="", help="OpenAI-compatible base URL when using a real provider.")
    qa_runtime_eval_parser.add_argument("--api-key-env", default="HTML_LORE_AI_API_KEY", help="Environment variable containing the real provider API key.")
    qa_runtime_eval_parser.add_argument("--model", default="fake-eval-model", help="Model name for evaluation.")
    qa_runtime_eval_parser.add_argument("--retrieval-mode", default="keyword", choices=["keyword", "vector", "hybrid"], help="Retrieval mode to evaluate.")
    qa_runtime_eval_parser.add_argument("--agent-no-model", action="store_true", help="Run the new QA agent without calling the model.")
    qa_runtime_eval_parser.add_argument("--agent-only", action="store_true", help="Only run the new QA agent.")
    qa_runtime_eval_parser.add_argument("--legacy-only", action="store_true", help="Only run the legacy QA graph.")
    qa_runtime_eval_parser.add_argument("--out", default="", help="Optional JSON output path. Defaults to stdout.")

    vector_parser = subparsers.add_parser("ai-vector-index", help="Maintain the local AI vector index.")
    vector_parser.add_argument("action", choices=["stats", "prune", "clear", "rebuild", "smoke-test"], help="Vector index maintenance action.")

    args = parser.parse_args(argv)
    if args.command == "build":
        manifest = build_site(
            content_dir=Path(args.content),
            meta_dir=Path(args.meta),
            output_dir=Path(args.out),
            site_title=args.title,
        )
        print(f"Built {len(manifest['items'])} items into {args.out}")
    elif args.command == "serve-api":
        try:
            import uvicorn
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency guard
            raise SystemExit("serve-api requires the agent extra: pip install 'html-lore[agent]'") from exc
        uvicorn.run("html_lore.server.app:app", host=args.host, port=args.port, reload=False)
    elif args.command == "user-add":
        settings = ServerSettings(
            content_dir=Path("data/content"),
            meta_dir=Path("data/meta"),
            public_dir=Path("public"),
            site_title="HTMlore",
            max_upload_bytes=10 * 1024 * 1024,
            users_file=Path(args.users_file),
        )
        try:
            user = UserStore(settings).add_user(
                username=args.username,
                password=args.password,
                role=args.role,
                data_id=args.data_id,
                replace_existing=args.replace,
            )
        except UserStoreError as exc:
            raise SystemExit(str(exc)) from exc
        print(f"Saved user {user['username']} with data partition {user['data_id']} in {args.users_file}")
    elif args.command == "ai-eval-qa":
        api_key = os.getenv(args.api_key_env, "") if args.provider != "fake" else ""
        report = run_knowledge_qa_eval(
            KnowledgeQAEvalSpec(
                content_dir=Path(args.content),
                meta_dir=Path(args.meta) if args.meta else None,
                public_dir=Path(args.public),
                questions=load_eval_questions(Path(args.questions) if args.questions else None),
                provider=args.provider,
                base_url=args.base_url,
                api_key=api_key,
                model=args.model,
                source_mode=args.source_mode,
                retrieval_mode=args.retrieval_mode,
            ),
        )
        payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(payload + "\n", encoding="utf-8")
            print(f"Wrote QA eval report to {args.out}")
        else:
            print(payload)
    elif args.command == "ai-eval-qa-runtime":
        if args.agent_only and args.legacy_only:
            raise SystemExit("--agent-only and --legacy-only cannot be used together.")
        api_key = os.getenv(args.api_key_env, "") if args.provider != "fake" else ""
        report = run_qa_runtime_eval(
            QARuntimeEvalSpec(
                content_dir=Path(args.content),
                meta_dir=Path(args.meta) if args.meta else None,
                public_dir=Path(args.public),
                cases=load_runtime_eval_cases(Path(args.cases) if args.cases else None),
                provider=args.provider,
                base_url=args.base_url,
                api_key=api_key,
                model=args.model,
                retrieval_mode=args.retrieval_mode,
                run_legacy=not args.agent_only,
                run_agent=not args.legacy_only,
                agent_uses_model=not args.agent_no_model,
            ),
        )
        payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(payload + "\n", encoding="utf-8")
            print(f"Wrote QA runtime eval report to {args.out}")
        else:
            print(payload)
    elif args.command == "ai-vector-index":
        settings = load_settings()
        service = vector_maintenance_for_config(ItemService(settings), AIProviderConfigStore(settings).get())
        try:
            if args.action == "stats":
                report = service.stats()
            elif args.action == "prune":
                report = service.prune()
            elif args.action == "clear":
                report = service.clear()
            elif args.action == "rebuild":
                report = service.rebuild()
            else:
                report = service.smoke_test_embedding()
        except VectorMaintenanceError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
