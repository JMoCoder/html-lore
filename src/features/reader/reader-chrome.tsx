"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { formatDate, noteReadingTime, shareUrl } from "@/features/workspace/note-meta";
import type { Note } from "@/fixtures/notes";

const PANEL_WIDTH = 320;

export function ReaderChrome({ note }: { note: Note }) {
  const params = useSearchParams();
  const [panelOpen, setPanelOpen] = useState(params.get("edit") === "1");
  const [editorOpen, setEditorOpen] = useState(params.get("edit") === "1");

  return (
    <div className="flex h-dvh flex-col bg-bg">
      <header className="flex h-12 shrink-0 items-center gap-2 border-b border-line px-3">
        <Link
          href="/"
          className="group inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-[13px] text-ink-soft transition-colors hover:bg-panel hover:text-ink"
        >
          <span className="inline-flex transition-transform duration-150 group-hover:-translate-x-0.5">
            <Icon.chevronLeft />
          </span>
          工作台
        </Link>
        <div className="mx-auto flex min-w-0 max-w-xl flex-1 items-center justify-center gap-2">
          <h1 className="truncate text-[14px] font-semibold tracking-tight text-ink">
            {note.title}
          </h1>
          <span className="shrink-0 text-[11px] text-ink-faint">
            {note.collection} · {formatDate(note.updated)} · {noteReadingTime(note)}
          </span>
        </div>
        <div className="flex items-center gap-0.5">
          <IconButton label="收藏" tone={note.favorite ? "active" : "default"}>
            <Icon.star filled={note.favorite} />
          </IconButton>
          <IconButton label="归档" onClick={() => alert("原型")}>
            <Icon.archive />
          </IconButton>
          <IconButton label="分享" tone={note.shareToken ? "active" : "default"} onClick={() => alert("原型：分享对话框")}>
            <Icon.share />
          </IconButton>
          <IconButton label="打开原文" onClick={() => window.open(`/raw/${note.slug}`, "_blank")}>
            <Icon.external />
          </IconButton>
          <div className="mx-1 h-5 w-px bg-line" />
          <IconButton
            label={panelOpen ? "收起面板" : "笔记信息与编辑"}
            tone={panelOpen ? "active" : "default"}
            onClick={() => setPanelOpen((v) => !v)}
          >
            <Icon.edit />
          </IconButton>
        </div>
      </header>

      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <iframe
          title={note.title}
          sandbox="allow-same-origin"
          srcDoc={note.html}
          className="min-w-0 flex-1 border-0 bg-panel"
        />

        <aside
          aria-hidden={!panelOpen}
          style={{ width: PANEL_WIDTH, marginRight: panelOpen ? 0 : -PANEL_WIDTH }}
          className="shrink-0 border-l border-line bg-sidebar transition-[margin] duration-200 ease-out"
        >
          <div
            className={`scroll-thin h-full w-[320px] overflow-y-auto p-4 transition duration-200 ease-out ${
              panelOpen ? "translate-x-0 opacity-100" : "translate-x-3 opacity-0"
            }`}
          >
            <div className="flex items-center justify-between">
              <h2 className="text-[11px] font-medium tracking-[0.08em] text-ink-faint">笔记信息</h2>
              <ThemeToggle />
            </div>
            <dl className="mt-3 space-y-3 text-[13px]">
              <div>
                <dt className="text-[11px] text-ink-faint">标题</dt>
                <dd className="mt-0.5 text-ink">{note.title}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-ink-faint">摘要</dt>
                <dd className="mt-0.5 text-ink-soft">{note.summary}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-ink-faint">集合</dt>
                <dd className="mt-0.5 text-ink">{note.collection}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-ink-faint">标签</dt>
                <dd className="mt-0.5 flex flex-wrap gap-1.5">
                  {note.tags.map((tag) => (
                    <span key={tag} className="rounded-md bg-panel-raised px-1.5 py-0.5 text-[11px] text-ink-soft">
                      #{tag}
                    </span>
                  ))}
                </dd>
              </div>
              <div>
                <dt className="text-[11px] text-ink-faint">状态</dt>
                <dd className="mt-0.5 text-ink-soft">
                  {[note.favorite && "已收藏", note.archived && "已归档", note.shareToken && "已分享"]
                    .filter(Boolean)
                    .join(" · ") || "正常"}
                </dd>
              </div>
            </dl>

            <div className="mt-5 border-t border-line pt-4">
              <button
                type="button"
                onClick={() => setEditorOpen((v) => !v)}
                className="flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left text-[13px] font-medium text-ink hover:bg-panel-raised"
              >
                {note.archived ? "已归档 · 编辑已锁定" : "编辑"}
                <Icon.chevronDown />
              </button>
              {editorOpen && !note.archived ? (
                <div className="mt-3 space-y-2 text-[13px] text-ink-soft">
                  <p className="rounded-lg border border-line bg-panel-raised p-3 text-[12px] leading-relaxed">
                    原型：这里将挂「源码编辑（CodeMirror）」和「保守可视化编辑」。保存前会做分享安全预检。
                  </p>
                  <div className="flex gap-2">
                    <button className="h-8 flex-1 rounded-[var(--radius-control)] border border-line text-[12px] hover:bg-panel-raised">
                      源码
                    </button>
                    <button className="h-8 flex-1 rounded-[var(--radius-control)] border border-line text-[12px] hover:bg-panel-raised">
                      可视化
                    </button>
                  </div>
                </div>
              ) : null}
            </div>

            {note.shareToken ? (
              <div className="mt-4 rounded-lg border border-line bg-panel-raised p-3">
                <p className="text-[11px] font-medium text-ink-faint">当前分享</p>
                <a
                  href={shareUrl(note.shareToken)}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 block truncate text-[12px] text-accent-strong hover:underline"
                >
                  /share/{note.shareToken}
                </a>
              </div>
            ) : null}
          </div>
        </aside>
      </div>
    </div>
  );
}
