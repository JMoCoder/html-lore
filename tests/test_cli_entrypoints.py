from pathlib import Path

import pytest

from html_lore.cli import main as lore_main
from html_lore.server.ai.langgraph_qa import langgraph_available


def test_html_lore_cli_help_uses_new_program_name(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        lore_main(["--help"])

    assert exc_info.value.code == 0
    assert "usage: html-lore" in capsys.readouterr().out


def test_html_lore_cli_ai_eval_qa_outputs_json(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    content_dir = tmp_path / "content"
    meta_dir = tmp_path / "meta"
    public_dir = tmp_path / "public"
    note_path = content_dir / "mcp.html"
    note_path.parent.mkdir(parents=True)
    (meta_dir / "items").mkdir(parents=True)
    public_dir.mkdir()
    note_path.write_text("<!doctype html><html><body><h1>MCP Security</h1><p>MCP tool authorization and risk control.</p></body></html>", encoding="utf-8")
    (meta_dir / "items" / "mcp.yml").write_text(
        "\n".join(
            [
                "title: MCP Security",
                "summary: MCP tool authorization and risk control.",
                "source_type: imported",
                "collection: AI",
                "tags:",
                "  - MCP",
                "",
            ],
        ),
        encoding="utf-8",
    )

    lore_main(
        [
            "ai-eval-qa",
            "--content",
            str(content_dir),
            "--meta",
            str(meta_dir),
            "--public",
            str(public_dir),
            "--provider",
            "fake",
            "--model",
            "fake-eval-model",
        ],
    )

    output = capsys.readouterr().out
    assert '"kind": "knowledge_qa_eval"' in output
    assert '"question_count": 3' in output
    assert not (meta_dir / "ai" / "conversations.json").exists()


def test_html_lore_cli_ai_eval_qa_runtime_outputs_comparison_json(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    content_dir = tmp_path / "content"
    meta_dir = tmp_path / "meta"
    public_dir = tmp_path / "public"
    note_path = content_dir / "mcp.html"
    cases_path = tmp_path / "cases.json"
    note_path.parent.mkdir(parents=True)
    (meta_dir / "items").mkdir(parents=True)
    public_dir.mkdir()
    note_path.write_text("<!doctype html><html><body><h1>MCP Security</h1><p>MCP tool authorization and risk control.</p></body></html>", encoding="utf-8")
    (meta_dir / "items" / "mcp.yml").write_text(
        "\n".join(
            [
                "title: MCP Security",
                "summary: MCP tool authorization and risk control.",
                "source_type: imported",
                "collection: AI",
                "tags:",
                "  - MCP",
                "",
            ],
        ),
        encoding="utf-8",
    )
    cases_path.write_text(
        '[{"id":"mcp-summary","question":"Summarize MCP security.","context":{"item_id":"mcp.html"}}]',
        encoding="utf-8",
    )

    lore_main(
        [
            "ai-eval-qa-runtime",
            "--content",
            str(content_dir),
            "--meta",
            str(meta_dir),
            "--public",
            str(public_dir),
            "--cases",
            str(cases_path),
            "--provider",
            "fake",
            "--model",
            "fake-eval-model",
            "--agent-only",
            "--agent-no-model",
        ],
    )

    output = capsys.readouterr().out
    assert '"kind": "qa_runtime_batch_eval"' in output
    assert '"case_count": 1' in output
    assert '"engines": [' in output
    assert '"agent"' in output
    assert '"legacy"' not in output
    assert not (meta_dir / "ai" / "conversations.json").exists()


def test_html_lore_cli_ai_eval_qa_runtime_rejects_conflicting_engine_flags() -> None:
    with pytest.raises(SystemExit) as exc_info:
        lore_main(["ai-eval-qa-runtime", "--agent-only", "--legacy-only", "--langgraph-only"])

    assert str(exc_info.value) == "--agent-only, --legacy-only, and --langgraph-only cannot be combined."


def test_html_lore_cli_ai_eval_qa_runtime_langgraph_only_is_not_empty(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    content_dir = tmp_path / "content"
    meta_dir = tmp_path / "meta"
    public_dir = tmp_path / "public"
    note_path = content_dir / "mcp.html"
    cases_path = tmp_path / "cases.json"
    note_path.parent.mkdir(parents=True)
    (meta_dir / "items").mkdir(parents=True)
    public_dir.mkdir()
    note_path.write_text("<!doctype html><html><body><h1>MCP Security</h1><p>MCP tool authorization and risk control.</p></body></html>", encoding="utf-8")
    (meta_dir / "items" / "mcp.yml").write_text(
        "\n".join(
            [
                "title: MCP Security",
                "summary: MCP tool authorization and risk control.",
                "source_type: imported",
                "collection: AI",
                "tags:",
                "  - MCP",
                "",
            ],
        ),
        encoding="utf-8",
    )
    cases_path.write_text('[{"id":"mcp-summary","question":"Summarize MCP security.","context":{"item_id":"mcp.html"}}]', encoding="utf-8")

    args = [
        "ai-eval-qa-runtime",
        "--content",
        str(content_dir),
        "--meta",
        str(meta_dir),
        "--public",
        str(public_dir),
        "--cases",
        str(cases_path),
        "--provider",
        "fake",
        "--model",
        "fake-eval-model",
        "--langgraph-only",
        "--agent-no-model",
    ]
    if not langgraph_available():
        with pytest.raises(SystemExit) as exc_info:
            lore_main(args)
        assert "LangGraph is not installed" in str(exc_info.value)
        return

    lore_main(args)
    output = capsys.readouterr().out
    assert '"langgraph"' in output
    assert '"LangGraphKnowledgeQA.v1"' in output
    assert '"results": {}' not in output
