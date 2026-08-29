"use client";

import { useEffect, useMemo, useState } from "react";
import { Icon } from "@/components/ui/icons";
import { formatDateTime } from "@/i18n";
import { useI18n } from "@/i18n/locale-provider";
import {
  createShareLink,
  isShareConfirmationRequired,
  listShares,
  revokeShareLink,
  updateShareLink,
  type PublicShare,
} from "@/lib/api";

export type ShareDuration = "1h" | "1d" | "7d" | "30d" | "forever";
export type ShareMode = "safe" | "interactive";

type Props = {
  open: boolean;
  itemId: string;
  title: string;
  interactiveEnabled?: boolean;
  onClose: () => void;
  onChanged?: () => void;
};

export function ShareDialog(props: Props) {
  const { locale, messages: t } = useI18n();
  const [duration, setDuration] = useState<ShareDuration>("1d");
  const [mode, setMode] = useState<ShareMode>("safe");
  const [awaitingConfirm, setAwaitingConfirm] = useState(false);
  const [modeHint, setModeHint] = useState<ShareMode | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");
  const [existing, setExisting] = useState<PublicShare | null>(null);

  const durations = useMemo(
    () =>
      [
        { id: "1h" as const, label: t.shareDialog.duration1h },
        { id: "1d" as const, label: t.shareDialog.duration1d },
        { id: "7d" as const, label: t.shareDialog.duration7d },
        { id: "30d" as const, label: t.shareDialog.duration30d },
        { id: "forever" as const, label: t.shareDialog.durationForever },
      ] as const,
    [t.shareDialog],
  );

  useEffect(() => {
    if (!props.open || !props.itemId) return;
    setError("");
    setFeedback("");
    setAwaitingConfirm(false);
    setModeHint(null);
    let cancelled = false;
    listShares()
      .then((body) => {
        if (cancelled) return;
        const active = body.shares.find((row) => row.item_id === props.itemId && row.active) ?? null;
        setExisting(active);
        setDuration(asDuration(active?.duration));
        setMode(active?.mode === "interactive" ? "interactive" : "safe");
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [props.open, props.itemId]);

  if (!props.open) return null;

  const shareUrl = existing?.url_path ? absoluteShareUrl(existing.url_path) : "";
  const hasShare = Boolean(existing);

  async function submit(confirmPrivateReferences = false) {
    setBusy(true);
    setError("");
    setFeedback("");
    try {
      if (existing) {
        const updated = await updateShareLink(existing.id, duration);
        setExisting(updated);
        setFeedback(t.shareDialog.updated);
      } else {
        try {
          const created = await createShareLink({
            itemId: props.itemId,
            duration,
            mode,
            confirmPrivateReferences,
          });
          setAwaitingConfirm(false);
          setExisting(created.share);
          setFeedback(t.shareDialog.created);
        } catch (err) {
          if (!confirmPrivateReferences && mode === "interactive" && isShareConfirmationRequired(err)) {
            setAwaitingConfirm(true);
            return;
          }
          throw err;
        }
      }
      props.onChanged?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : t.shareDialog.createFailed);
    } finally {
      setBusy(false);
    }
  }

  async function revoke() {
    if (!existing) return;
    setBusy(true);
    setError("");
    setFeedback("");
    try {
      await revokeShareLink(existing.id);
      setExisting(null);
      setDuration("1d");
      setMode("safe");
      setFeedback(t.shareDialog.revoked);
      props.onChanged?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : t.shareDialog.createFailed);
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    if (!shareUrl) return;
    await navigator.clipboard.writeText(shareUrl);
    setFeedback(t.shareDialog.copied);
  }

  return (
    <div className="fixed inset-0 z-[60] grid place-items-center bg-ink/20 px-4 backdrop-blur-[2px]" onClick={props.onClose}>
      <div
        className="w-full max-w-[400px] rounded-[var(--radius-card)] border border-line bg-panel p-5 shadow-[var(--shadow-card)]"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="share-dialog-title"
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 id="share-dialog-title" className="text-[15px] font-semibold tracking-tight text-ink">
              {t.shareDialog.title}
            </h2>
            <p className="mt-1 line-clamp-2 text-[12px] text-ink-soft">{props.title}</p>
          </div>
          <button type="button" onClick={props.onClose} className="rounded-lg p-1 text-ink-faint hover:bg-panel-raised hover:text-ink">
            <Icon.x />
          </button>
        </div>

        <label className="mt-4 block text-[11px] text-ink-faint">
          {t.shareDialog.duration}
          <select
            value={duration}
            onChange={(e) => setDuration(e.target.value as ShareDuration)}
            className="mt-1 h-9 w-full rounded-[var(--radius-control)] border border-line bg-panel-raised px-3 text-[13px] text-ink outline-none focus:border-accent/60"
          >
            {durations.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        <div className="mt-3">
          <p className="text-[11px] text-ink-faint">{t.shareDialog.mode}</p>
          <div className="mt-1 flex gap-1 rounded-lg bg-sidebar p-0.5">
            {(["safe", "interactive"] as const).map((value) => {
              const selected = mode === value;
              const hint = value === "safe" ? t.shareDialog.modeSafeHint : t.shareDialog.modeInteractiveHint;
              return (
                <div
                  key={value}
                  className={`flex min-w-0 flex-1 items-center rounded-md ${
                    selected ? "bg-panel-raised text-ink shadow-[var(--shadow-sm)]" : "text-ink-faint"
                  }`}
                >
                  <button
                    type="button"
                    disabled={hasShare || (value === "interactive" && !props.interactiveEnabled)}
                    onClick={() => {
                      setMode(value);
                      setAwaitingConfirm(false);
                    }}
                    className="h-8 min-w-0 flex-1 truncate rounded-md px-1 text-[12px] disabled:opacity-40"
                  >
                    {value === "safe" ? t.shareDialog.modeSafe : t.shareDialog.modeInteractive}
                  </button>
                  <ModeHelpButton
                    label={value === "safe" ? t.shareDialog.modeSafeHelp : t.shareDialog.modeInteractiveHelp}
                    hint={hint}
                    open={modeHint === value}
                    onClick={() => setModeHint((current) => (current === value ? null : value))}
                  />
                </div>
              );
            })}
          </div>
          {modeHint ? (
            <p className="mt-1.5 text-[11px] leading-4 text-ink-soft">
              {modeHint === "safe" ? t.shareDialog.modeSafeHint : t.shareDialog.modeInteractiveHint}
            </p>
          ) : null}
        </div>

        {shareUrl ? (
          <div className="mt-4 rounded-lg border border-line bg-panel-raised p-3">
            <p className="text-[11px] font-medium text-ink-faint">{t.shareDialog.link}</p>
            <a href={shareUrl} target="_blank" rel="noreferrer" className="mt-1 block truncate text-[12px] text-accent-strong hover:underline">
              {shareUrl}
            </a>
            <p className="mt-1 text-[11px] text-ink-faint">
              {existing?.expires_at ? t.shareDialog.expiresAt(formatDateTime(existing.expires_at, locale)) : t.shareDialog.noExpiry}
            </p>
            <button type="button" onClick={copy} className="mt-2 text-[11px] text-ink-soft hover:text-ink">
              {t.shareDialog.copyLink}
            </button>
          </div>
        ) : null}

        {feedback ? <p className="mt-3 text-[12px] text-ink-soft">{feedback}</p> : null}
        {error ? <p className="mt-3 text-[12px] text-danger">{error}</p> : null}

        <div className="mt-5 flex items-center justify-end gap-2">
          {hasShare ? (
            <button
              type="button"
              disabled={busy}
              onClick={revoke}
              className="mr-auto h-9 rounded-[var(--radius-control)] px-3 text-[13px] text-danger hover:bg-danger/10 disabled:opacity-60"
            >
              {t.shareDialog.revoke}
            </button>
          ) : null}
          <button type="button" onClick={props.onClose} className="h-9 rounded-[var(--radius-control)] px-3 text-[13px] text-ink-soft hover:bg-panel-raised">
            {t.shareDialog.close}
          </button>
          <button
            type="button"
            disabled={busy || awaitingConfirm}
            onClick={() => void submit()}
            className="h-9 rounded-[var(--radius-control)] bg-accent px-4 text-[13px] font-medium text-white hover:bg-accent-strong disabled:opacity-60"
          >
            {busy ? t.shareDialog.saving : hasShare ? t.shareDialog.update : t.shareDialog.create}
          </button>
        </div>
      </div>

      {awaitingConfirm ? (
        <div
          className="absolute inset-0 z-[1] grid place-items-center bg-ink/25 px-4"
          onClick={(e) => {
            e.stopPropagation();
            if (!busy) setAwaitingConfirm(false);
          }}
        >
          <div
            className="w-full max-w-[360px] rounded-[var(--radius-card)] border border-line bg-panel p-5 shadow-[var(--shadow-card)]"
            onClick={(e) => e.stopPropagation()}
            role="alertdialog"
            aria-labelledby="share-confirm-title"
            aria-describedby="share-confirm-body"
          >
            <h3 id="share-confirm-title" className="text-[15px] font-semibold tracking-tight text-ink">
              {t.shareDialog.confirmPrivateTitle}
            </h3>
            <p id="share-confirm-body" className="mt-2 text-[13px] leading-5 text-ink-soft">
              {t.shareDialog.confirmPrivate}
            </p>
            <div className="mt-5 flex items-center justify-end gap-2">
              <button
                type="button"
                disabled={busy}
                onClick={() => setAwaitingConfirm(false)}
                className="h-9 rounded-[var(--radius-control)] px-3 text-[13px] text-ink-soft hover:bg-panel-raised disabled:opacity-60"
              >
                {t.shareDialog.confirmPrivateCancel}
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => void submit(true)}
                className="h-9 rounded-[var(--radius-control)] bg-accent px-4 text-[13px] font-medium text-white hover:bg-accent-strong disabled:opacity-60"
              >
                {busy ? t.shareDialog.saving : t.shareDialog.confirmPrivateSubmit}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function ModeHelpButton({
  label,
  hint,
  open,
  onClick,
}: {
  label: string;
  hint: string;
  open: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      aria-expanded={open}
      title={hint}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      className={`mr-0.5 inline-flex size-[18px] shrink-0 items-center justify-center rounded-full hover:bg-sidebar hover:text-ink ${
        open ? "text-ink" : "text-ink-faint"
      }`}
    >
      <span className="[&>svg]:size-3.5">
        <Icon.help />
      </span>
    </button>
  );
}

function asDuration(value: string | undefined): ShareDuration {
  if (value === "1h" || value === "1d" || value === "7d" || value === "30d" || value === "forever") return value;
  return "1d";
}

function absoluteShareUrl(path: string) {
  try {
    return new URL(path, window.location.origin).href;
  } catch {
    return path;
  }
}
