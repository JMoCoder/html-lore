"use client";

import { useEffect, useMemo, useState } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { html } from "@codemirror/lang-html";
import { indentWithTab } from "@codemirror/commands";
import { EditorView, keymap } from "@codemirror/view";

function editorTheme(dark: boolean) {
  return EditorView.theme(
    {
      "&": {
        height: "100%",
        backgroundColor: "var(--panel)",
        color: "var(--ink)",
      },
      ".cm-scroller": { fontFamily: "var(--font-mono)", overflow: "auto" },
      ".cm-content": { fontSize: "13px", lineHeight: "1.55", padding: "16px 0" },
      ".cm-gutters": {
        backgroundColor: "var(--panel)",
        color: "var(--ink-faint)",
        border: "none",
        borderRight: "1px solid var(--line)",
      },
      ".cm-activeLineGutter": { backgroundColor: "var(--panel-raised)" },
      "&.cm-focused .cm-cursor": { borderLeftColor: "var(--accent)" },
      "&.cm-focused .cm-selectionBackground, .cm-selectionBackground": {
        backgroundColor: "var(--accent-soft) !important",
      },
    },
    { dark },
  );
}

export function HtmlSourceEditor({
  value,
  onChange,
  wrap = true,
  onCursor,
}: {
  value: string;
  onChange: (value: string) => void;
  wrap?: boolean;
  onCursor?: (position: { line: number; column: number }) => void;
}) {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    const sync = () => setDark(root.classList.contains("dark"));
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(root, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

  const extensions = useMemo(
    () => [
      html(),
      editorTheme(dark),
      keymap.of([indentWithTab]),
      ...(wrap ? [EditorView.lineWrapping] : []),
      EditorView.updateListener.of((update) => {
        if (!onCursor || (!update.selectionSet && !update.docChanged)) return;
        const head = update.state.selection.main.head;
        const line = update.state.doc.lineAt(head);
        onCursor({ line: line.number, column: head - line.from + 1 });
      }),
    ],
    [dark, wrap, onCursor],
  );

  return (
    <div className="html-source-editor h-full min-h-0">
      <CodeMirror
        value={value}
        height="100%"
        className="h-full min-h-0"
        extensions={extensions}
        onChange={onChange}
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          highlightActiveLine: true,
          autocompletion: false,
          indentOnInput: true,
        }}
      />
    </div>
  );
}
