"use client";

import { useEffect, useMemo, useState, useSyncExternalStore, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import { LanguageSwitcher } from "@/components/ui/language-switcher";
import { applyTheme, isDarkTheme, THEME_CHANGE_EVENT } from "@/components/ui/theme";
import type { LibraryFilter } from "@/fixtures/notes";
import { formatDateTime } from "@/i18n";
import { useI18n } from "@/i18n/locale-provider";
import { apiJson, readHref, triggerDownload } from "@/lib/api";
import { emptyNavConfig, isNavVisible, setNavVisible, type NavConfig } from "@/lib/navigation";
import type { Item } from "@/server/types";
import { APP_VERSION } from "@/server/version";

type Tab = "basic" | "library" | "collections" | "tags" | "export" | "shares" | "terms" | "about";

type Entry = { name: string; count: number };

export type ManagedShare = {
  id: string;
  item_id: string;
  url_path: string;
  active: boolean;
  revoked: boolean;
  expires_at: string;
  access_count: number;
  mode: string;
  created_at: string;
  updated_at: string;
};

type Props = {
  onClose: () => void;
  navConfig: NavConfig | null;
  onNavConfig: (config: NavConfig) => void;
  items: Item[];
  collections: Entry[];
  allTags: Entry[];
  libraryCounts: Record<LibraryFilter, number>;
  onItemsChanged: () => void;
  onRenamed?: (kind: "collection" | "tag", from: string, to: string) => void;
  onSharesChanged: () => void;
  shareEpoch?: number;
  onManageShare: (itemId: string) => void;
};

const LIBRARY_ORDER: LibraryFilter[] = ["all", "recent", "favorites", "imported", "archived"];

export function SettingsPage(props: Props) {
  const router = useRouter();
  const { locale, messages: t } = useI18n();
  const [tab, setTab] = useState<Tab>("basic");
  const [savingNav, setSavingNav] = useState(false);
  const [renameMessage, setRenameMessage] = useState("");
  const [exportMessage, setExportMessage] = useState("");
  const [shares, setShares] = useState<ManagedShare[]>([]);
  const [shareMessage, setShareMessage] = useState("");
  const [version, setVersion] = useState(APP_VERSION);

  const config = props.navConfig ?? emptyNavConfig();

  const onClose = props.onClose;

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  useEffect(() => {
    apiJson<{ version?: string }>("/api/version")
      .then((body) => {
        if (body.version) setVersion(body.version);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (tab !== "shares") return;
    apiJson<{ shares: ManagedShare[] }>("/api/shares")
      .then((body) => setShares(body.shares))
      .catch(() => setShareMessage(t.settings.loadFailed));
  }, [tab, t.settings.loadFailed, props.shareEpoch]);

  const libraryRows = useMemo(
    () =>
      LIBRARY_ORDER.map((id) => ({
        id,
        label:
          id === "all"
            ? t.sidebar.all
            : id === "recent"
              ? t.sidebar.recent
              : id === "favorites"
                ? t.sidebar.favorites
                : id === "imported"
                  ? t.sidebar.imported
                  : t.sidebar.archived,
      })),
    [t.sidebar],
  );

  const visibleShares = useMemo(
    () =>
      shares
        .filter((share) => !share.revoked)
        .sort((left, right) => {
          if (left.active !== right.active) return left.active ? -1 : 1;
          return String(right.updated_at || right.created_at).localeCompare(String(left.updated_at || left.created_at));
        }),
    [shares],
  );

  async function toggleVisible(section: keyof NavConfig, name: string, visible: boolean) {
    const next = setNavVisible(config, section, name, visible);
    setSavingNav(true);
    try {
      const saved = await apiJson<NavConfig>("/api/navigation", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(next),
      });
      props.onNavConfig(saved);
    } finally {
      setSavingNav(false);
    }
  }

  async function renameEntry(kind: "collection" | "tag", from: string, to: string) {
    setRenameMessage("");
    setSavingNav(true);
    try {
      const result = await apiJson<{ from: string; to: string }>("/api/taxonomy/rename", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind, from, to }),
      });
      props.onRenamed?.(kind, result.from, result.to);
      props.onItemsChanged();
    } catch {
      setRenameMessage(t.settings.renameFailed);
    } finally {
      setSavingNav(false);
    }
  }

  function startExport(kind: "manifest" | "archive") {
    setExportMessage("");
    try {
      triggerDownload(kind === "manifest" ? "/api/export/manifest" : "/api/export/archive");
      setExportMessage(t.settings.exportStarted);
    } catch {
      setExportMessage(t.settings.exportFailed);
    }
  }

  async function revokeShare(share: ManagedShare) {
    setShareMessage("");
    try {
      await apiJson(`/api/shares/${encodeURIComponent(share.id)}`, { method: "DELETE" });
      setShares((current) => current.map((row) => (row.id === share.id ? { ...row, revoked: true, active: false } : row)));
      setShareMessage(t.settings.shareRevokedOk);
      props.onSharesChanged();
    } catch {
      setShareMessage(t.settings.shareFailed);
    }
  }

  const navItems: { id: Tab; label: string; divider?: boolean }[] = [
    { id: "basic", label: t.settings.basic },
    { id: "library", label: t.settings.library, divider: true },
    { id: "collections", label: t.settings.collections },
    { id: "tags", label: t.settings.tags },
    { id: "export", label: t.settings.export, divider: true },
    { id: "shares", label: t.settings.shares },
    { id: "terms", label: t.settings.terms, divider: true },
    { id: "about", label: t.settings.about },
  ];

  return (
    <div className="app-shell fixed inset-0 z-50 flex flex-col bg-bg">
      <header className="flex h-14 shrink-0 items-center gap-2 border-b border-line px-3 md:px-4">
        <IconButton label={t.settings.close} onClick={props.onClose}>
          <Icon.chevronLeft />
        </IconButton>
        <h1 className="text-[15px] font-semibold tracking-tight text-ink">{t.settings.title}</h1>
      </header>

      <nav
        aria-label={t.settings.sections}
        className="scroll-thin flex shrink-0 gap-1 overflow-x-auto border-b border-line px-3 py-2 md:hidden"
      >
        {navItems.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setTab(item.id)}
            className={`h-10 shrink-0 rounded-[var(--radius-control)] px-3 text-[13px] ${
              tab === item.id ? "bg-accent-soft font-medium text-accent-strong" : "text-ink-soft"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="flex min-h-0 flex-1">
        <nav
          aria-label={t.settings.sections}
          className="hidden w-[252px] shrink-0 flex-col border-r border-line bg-sidebar py-3 md:flex"
        >
          {navItems.map((item) => (
            <div key={item.id}>
              {item.divider ? <div className="mx-3 my-2 h-px bg-line" /> : null}
              <button
                type="button"
                onClick={() => setTab(item.id)}
                className={`mb-0.5 flex h-8 w-full items-center rounded-lg px-3 text-left text-[13px] transition-all ${
                  tab === item.id
                    ? "bg-panel-raised font-medium text-ink shadow-[var(--shadow-sm)]"
                    : "text-ink-soft hover:bg-panel-raised/70 hover:text-ink"
                }`}
              >
                {item.label}
              </button>
            </div>
          ))}
        </nav>

        <section className="scroll-thin min-w-0 flex-1 overflow-y-auto px-4 py-5 md:px-8 md:py-6">
          <div className="mx-auto w-full max-w-[640px]">
            {tab === "basic" ? (
              <Section title={t.settings.basic} intro={t.settings.basicIntro}>
                <Field label={t.settings.language}>
                  <LanguageSwitcher />
                </Field>
                <Field label={t.settings.theme}>
                  <ThemeModeButtons />
                </Field>
              </Section>
            ) : null}

            {tab === "library" ? (
              <Section title={t.settings.library} intro={t.settings.libraryIntro}>
                <ManagementList
                  rows={libraryRows.map((row) => ({
                    name: row.id,
                    label: row.label,
                    visible: isNavVisible(config, "library", row.id),
                  }))}
                  visibleLabel={t.settings.visible}
                  empty={t.settings.emptyList}
                  disabled={savingNav}
                  onToggle={(name, visible) => toggleVisible("library", name, visible)}
                />
              </Section>
            ) : null}

            {tab === "collections" ? (
              <Section title={t.settings.collections} intro={t.settings.collectionsIntro}>
                <ManagementList
                  rows={props.collections.map((row) => ({
                    name: row.name,
                    label: row.name,
                    visible: isNavVisible(config, "collections", row.name),
                  }))}
                  visibleLabel={t.settings.visible}
                  empty={t.settings.emptyList}
                  disabled={savingNav}
                  onToggle={(name, visible) => toggleVisible("collections", name, visible)}
                  onRename={(from, to) => renameEntry("collection", from, to)}
                  renameLabel={t.settings.rename}
                  renameSave={t.settings.renameSave}
                  renameCancel={t.settings.renameCancel}
                  renamePlaceholder={t.settings.renamePlaceholder}
                />
                {renameMessage && tab === "collections" ? <p className="mt-3 text-[12px] text-ink-soft">{renameMessage}</p> : null}
              </Section>
            ) : null}

            {tab === "tags" ? (
              <Section title={t.settings.tags} intro={t.settings.tagsIntro}>
                <ManagementList
                  rows={props.allTags.map((row) => ({
                    name: row.name,
                    label: `#${row.name}`,
                    visible: isNavVisible(config, "tags", row.name),
                  }))}
                  visibleLabel={t.settings.visible}
                  empty={t.settings.emptyList}
                  disabled={savingNav}
                  onToggle={(name, visible) => toggleVisible("tags", name, visible)}
                  onRename={(from, to) => renameEntry("tag", from, to)}
                  renameLabel={t.settings.rename}
                  renameSave={t.settings.renameSave}
                  renameCancel={t.settings.renameCancel}
                  renamePlaceholder={t.settings.renamePlaceholder}
                />
                {renameMessage && tab === "tags" ? <p className="mt-3 text-[12px] text-ink-soft">{renameMessage}</p> : null}
              </Section>
            ) : null}

            {tab === "export" ? (
              <Section title={t.settings.export} intro={t.settings.exportIntro}>
                <div className="mt-5 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => startExport("manifest")}
                    className="h-9 rounded-[var(--radius-control)] bg-accent px-3 text-[13px] font-medium text-white hover:bg-accent-strong"
                  >
                    {t.settings.exportManifest}
                  </button>
                  <button
                    type="button"
                    onClick={() => startExport("archive")}
                    className="h-9 rounded-[var(--radius-control)] border border-line bg-panel px-3 text-[13px] text-ink hover:bg-panel-raised"
                  >
                    {t.settings.exportHtml}
                  </button>
                </div>
                <p className="mt-4 text-[12px] leading-5 text-ink-faint">{t.settings.exportNote}</p>
                {exportMessage ? <p className="mt-3 text-[12px] text-ink-soft">{exportMessage}</p> : null}
              </Section>
            ) : null}

            {tab === "shares" ? (
              <Section title={t.settings.shares} intro={t.settings.sharesIntro}>
                {visibleShares.length === 0 ? (
                  <p className="mt-6 text-[13px] text-ink-faint">{t.settings.noShares}</p>
                ) : (
                  <ul className="mt-5 space-y-2">
                    {visibleShares.map((share) => {
                      const item = props.items.find((row) => row.id === share.item_id);
                      const title = item?.title || share.item_id;
                      return (
                        <li
                          key={share.id}
                          className="rounded-[var(--radius-card)] border border-line bg-panel px-4 py-3"
                        >
                          <div className="flex items-start justify-between gap-3 max-md:flex-col">
                            <div className="min-w-0">
                              {item ? (
                                <button
                                  type="button"
                                  className="block truncate text-left text-[13px] font-medium text-ink hover:text-accent"
                                  onClick={() => {
                                    props.onClose();
                                    router.push(readHref(item.id));
                                  }}
                                >
                                  {title}
                                </button>
                              ) : (
                                <p className="truncate text-[13px] font-medium text-ink">{title}</p>
                              )}
                              <p className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px] text-ink-faint">
                                <StatusPill active={share.active} activeLabel={t.settings.shareActive} expiredLabel={t.settings.shareExpired} />
                                <span>{share.expires_at ? formatDateTime(share.expires_at, locale) : t.settings.shareNoExpiry}</span>
                                <span>{t.settings.shareAccessCount(share.access_count || 0)}</span>
                                <span>{share.mode}</span>
                              </p>
                            </div>
                            <div className="flex shrink-0 items-center gap-1 max-md:w-full max-md:justify-end">
                              <button
                                type="button"
                                className="h-8 rounded-[var(--radius-control)] px-2.5 text-[12px] text-ink-soft hover:bg-panel-raised hover:text-ink"
                                onClick={() => {
                                  if (item) props.onManageShare(item.id);
                                }}
                              >
                                {t.settings.openShare}
                              </button>
                              <button
                                type="button"
                                className="h-8 rounded-[var(--radius-control)] px-2.5 text-[12px] text-danger hover:bg-danger/10"
                                onClick={() => revokeShare(share)}
                              >
                                {t.settings.revokeShare}
                              </button>
                            </div>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                )}
                {shareMessage ? <p className="mt-3 text-[12px] text-ink-soft">{shareMessage}</p> : null}
              </Section>
            ) : null}

            {tab === "terms" ? (
              <Section title={t.settings.terms} intro={t.settings.termsIntro}>
                <ul className="mt-5 space-y-3 text-[13px] leading-6 text-ink-soft">
                  <li>{t.settings.termsPrivateUse}</li>
                  <li>{t.settings.termsCopyright}</li>
                  <li>{t.settings.termsSecurity}</li>
                </ul>
              </Section>
            ) : null}

            {tab === "about" ? (
              <Section title={t.settings.about} intro={t.settings.aboutIntro}>
                <p className="mt-5 text-[13px] leading-6 text-ink-soft">{t.settings.aboutStaticFirst}</p>
                <p className="mt-3 text-[13px] text-ink">{t.settings.aboutVersion(version)}</p>
                <a
                  href="https://github.com/JMoCoder/html-lore"
                  target="_blank"
                  rel="noreferrer"
                  className="mt-4 inline-flex h-9 items-center rounded-[var(--radius-control)] border border-line bg-panel px-3 text-[13px] text-ink hover:bg-panel-raised"
                >
                  {t.settings.aboutRepo}
                </a>
              </Section>
            ) : null}
          </div>
        </section>
      </div>
    </div>
  );
}

function Section({ title, intro, children }: { title: string; intro: string; children: ReactNode }) {
  return (
    <div>
      <h2 className="text-[15px] font-semibold tracking-tight text-ink">{title}</h2>
      <p className="mt-1 text-[12px] leading-5 text-ink-soft">{intro}</p>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="mt-5">
      <p className="mb-1.5 text-[11px] font-medium tracking-[0.08em] text-ink-faint">{label}</p>
      {children}
    </div>
  );
}

function ThemeModeButtons() {
  const { messages: t } = useI18n();
  const dark = useSyncExternalStore(
    (onStoreChange) => {
      window.addEventListener(THEME_CHANGE_EVENT, onStoreChange);
      return () => window.removeEventListener(THEME_CHANGE_EVENT, onStoreChange);
    },
    isDarkTheme,
    () => false,
  );

  return (
    <div className="inline-flex h-9 rounded-[var(--radius-control)] border border-line bg-panel p-0.5">
      <button
        type="button"
        onClick={() => applyTheme(false)}
        className={`h-8 rounded-[8px] px-3 text-[12px] ${dark ? "text-ink-soft hover:text-ink" : "bg-panel-raised font-medium text-ink shadow-[var(--shadow-sm)]"}`}
      >
        {t.settings.themeLight}
      </button>
      <button
        type="button"
        onClick={() => applyTheme(true)}
        className={`h-8 rounded-[8px] px-3 text-[12px] ${dark ? "bg-panel-raised font-medium text-ink shadow-[var(--shadow-sm)]" : "text-ink-soft hover:text-ink"}`}
      >
        {t.settings.themeDark}
      </button>
    </div>
  );
}

function ManagementList({
  rows,
  visibleLabel,
  empty,
  disabled,
  onToggle,
  onRename,
  renameLabel,
  renameSave,
  renameCancel,
  renamePlaceholder,
}: {
  rows: { name: string; label: string; visible: boolean }[];
  visibleLabel: string;
  empty: string;
  disabled: boolean;
  onToggle: (name: string, visible: boolean) => void;
  onRename?: (from: string, to: string) => void;
  renameLabel?: string;
  renameSave?: string;
  renameCancel?: string;
  renamePlaceholder?: string;
}) {
  const [editing, setEditing] = useState("");
  const [draft, setDraft] = useState("");

  if (rows.length === 0) {
    return <p className="mt-6 text-[13px] text-ink-faint">{empty}</p>;
  }

  function commit(from: string) {
    const next = draft.trim();
    setEditing("");
    if (!next || next === from) return;
    onRename?.(from, next);
  }

  return (
    <ul className="mt-5 divide-y divide-line rounded-[var(--radius-card)] border border-line bg-panel">
      {rows.map((row) => (
        <li key={row.name} className="flex min-h-11 items-center gap-3 px-3 py-2 md:px-4 md:py-1.5">
          {editing === row.name ? (
            <form
              className="flex min-w-0 flex-1 items-center gap-2"
              onSubmit={(event) => {
                event.preventDefault();
                commit(row.name);
              }}
            >
              <input
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder={renamePlaceholder}
                autoFocus
                disabled={disabled}
                className="h-8 min-w-0 flex-1 rounded-md border border-line bg-panel-raised px-2 text-[13px] text-ink-soft outline-none focus:border-accent/60"
              />
              <button type="submit" disabled={disabled} className="h-8 shrink-0 rounded-md px-2 text-[12px] text-accent hover:bg-accent-soft">
                {renameSave}
              </button>
              <button
                type="button"
                disabled={disabled}
                className="h-8 shrink-0 rounded-md px-2 text-[12px] text-ink-faint/70 hover:bg-panel-raised"
                onClick={() => setEditing("")}
              >
                {renameCancel}
              </button>
            </form>
          ) : (
            <span className="min-w-0 flex-1 truncate text-[13px] text-ink-soft">{row.label}</span>
          )}
          {onRename && editing !== row.name ? (
            <button
              type="button"
              disabled={disabled}
              className="shrink-0 text-[12px] text-ink-faint/55 hover:text-ink-faint"
              onClick={() => {
                setEditing(row.name);
                setDraft(row.name);
              }}
            >
              {renameLabel}
            </button>
          ) : null}
          <label className="inline-flex shrink-0 cursor-pointer items-center gap-1.5 text-[12px] text-ink-faint/55">
            <span>{visibleLabel}</span>
            <input
              type="checkbox"
              className="size-4 accent-[var(--accent)]"
              checked={row.visible}
              disabled={disabled}
              onChange={(event) => onToggle(row.name, event.target.checked)}
            />
          </label>
        </li>
      ))}
    </ul>
  );
}

function StatusPill({
  active,
  activeLabel,
  expiredLabel,
}: {
  active: boolean;
  activeLabel: string;
  expiredLabel: string;
}) {
  return (
    <span
      className={`rounded-full px-1.5 py-0.5 text-[10px] font-medium tracking-wide ${
        active ? "bg-accent-soft text-accent-strong" : "bg-line text-ink-faint"
      }`}
    >
      {active ? activeLabel : expiredLabel}
    </span>
  );
}
