"use client";

import { useMemo, useState } from "react";
import { commitDraftTag, consumeHashTags, mergeTags, normalizeTagName } from "@/lib/tag-input";
import { useI18n } from "@/i18n/locale-provider";

const fieldClass =
  "mt-0.5 min-h-8 w-full rounded-md border border-line bg-panel px-2 py-1 text-[13px] text-ink outline-none focus-within:border-accent/60";

export function TagField({
  value,
  options,
  disabled,
  onChange,
}: {
  value: string[];
  options: string[];
  disabled?: boolean;
  onChange: (value: string[]) => void;
}) {
  const { messages: t } = useI18n();
  const [draft, setDraft] = useState("");

  const suggestions = useMemo(() => {
    const needle = normalizeTagName(draft).toLowerCase();
    return options
      .filter((name) => !value.includes(name))
      .filter((name) => !needle || name.toLowerCase().includes(needle))
      .slice(0, 12);
  }, [draft, options, value]);

  function addTags(incoming: string[]) {
    const next = mergeTags(value, incoming.map(normalizeTagName).filter(Boolean));
    if (next.length !== value.length) onChange(next);
  }

  function applyDraft(nextDraft: string) {
    const consumed = consumeHashTags(nextDraft);
    if (consumed.tags.length) addTags(consumed.tags);
    setDraft(consumed.draft);
  }

  function commitDraft() {
    const tag = commitDraftTag(draft);
    if (tag) addTags([tag]);
    setDraft("");
  }

  function removeTag(name: string) {
    onChange(value.filter((tag) => tag !== name));
  }

  return (
    <div>
      <div className={`${fieldClass} ${disabled ? "opacity-50" : ""}`}>
        <div className="flex flex-wrap items-center gap-1">
          {value.map((tag) => (
            <button
              key={tag}
              type="button"
              disabled={disabled}
              onClick={() => removeTag(tag)}
              className="inline-flex h-6 items-center gap-1 rounded-md bg-accent-soft px-1.5 text-[11px] font-medium text-accent-strong hover:bg-accent/15 disabled:pointer-events-none"
              title={t.reader.removeTag}
            >
              #{tag}
              <span aria-hidden className="text-accent-strong/70">
                ×
              </span>
            </button>
          ))}
          <input
            disabled={disabled}
            value={draft}
            placeholder={value.length ? t.reader.tagsPlaceholderMore : t.reader.tagsPlaceholder}
            aria-label={t.reader.tags}
            onChange={(event) => applyDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === "Tab") {
                if (!draft.trim()) return;
                event.preventDefault();
                commitDraft();
              } else if (event.key === "Backspace" && !draft && value.length) {
                event.preventDefault();
                removeTag(value[value.length - 1]);
              }
            }}
            onBlur={() => {
              if (draft.trim()) commitDraft();
            }}
            className="h-6 min-w-[7rem] flex-1 bg-transparent text-[13px] text-ink outline-none placeholder:text-ink-faint"
          />
        </div>
      </div>
      <p className="mt-1 text-[11px] text-ink-faint">{t.reader.tagsHint}</p>
      {suggestions.length ? (
        <div className="mt-1.5 flex flex-wrap gap-1">
          {suggestions.map((name) => (
            <button
              key={name}
              type="button"
              disabled={disabled}
              onClick={() => {
                addTags([name]);
                setDraft("");
              }}
              className="inline-flex h-6 items-center rounded-md border border-line px-1.5 text-[11px] text-ink-soft hover:border-accent/40 hover:bg-accent-soft hover:text-accent-strong disabled:opacity-50"
            >
              #{name}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
