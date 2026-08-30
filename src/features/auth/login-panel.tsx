"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { Logo } from "@/components/ui/logo";
import { LanguageSwitcher } from "@/components/ui/language-switcher";
import { apiJson } from "@/lib/api";
import { useI18n } from "@/i18n/locale-provider";

export function LoginPanel() {
  const router = useRouter();
  const { messages: t } = useI18n();
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await apiJson("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: String(form.get("username") || ""),
          password: String(form.get("password") || ""),
        }),
      });
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : t.login.failed);
    }
  }

  return (
    <main className="app-shell grid place-items-center bg-bg px-5">
      <div className="w-full max-w-[360px]">
        <div className="flex justify-center">
          <Logo size={26} />
        </div>
        <form
          onSubmit={onSubmit}
          className="mt-6 rounded-[var(--radius-card)] border border-line bg-panel p-6 shadow-[var(--shadow-sm)]"
        >
          <div className="flex items-start justify-between gap-3">
            <h1 className="text-[15px] font-semibold tracking-tight">{t.login.title}</h1>
            <LanguageSwitcher compact />
          </div>
          <label className="mt-5 block text-xs text-ink-soft">
            {t.login.username}
            <input
              name="username"
              autoComplete="username"
              className="mt-1.5 h-9 w-full rounded-[var(--radius-control)] border border-line bg-panel-raised px-3 text-[13px] outline-none focus:border-accent/60"
            />
          </label>
          <label className="mt-3 block text-xs text-ink-soft">
            {t.login.password}
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              className="mt-1.5 h-9 w-full rounded-[var(--radius-control)] border border-line bg-panel-raised px-3 text-[13px] outline-none focus:border-accent/60"
            />
          </label>
          {error ? <p className="mt-3 text-[12px] text-danger">{error}</p> : null}
          <button
            type="submit"
            className="mt-5 h-9 w-full rounded-[var(--radius-control)] bg-accent text-[13px] font-medium text-white transition-colors hover:bg-accent-strong max-md:h-11"
          >
            {t.login.submit}
          </button>
          <p className="mt-3 text-center text-[11px] text-ink-faint">{t.login.openHint}</p>
        </form>
      </div>
    </main>
  );
}
