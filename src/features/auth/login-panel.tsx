"use client";

import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { Logo } from "@/components/ui/logo";

export function LoginPanel() {
  const router = useRouter();

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    router.push("/");
  }

  return (
    <main className="grid min-h-dvh place-items-center bg-bg px-5">
      <div className="w-full max-w-[360px]">
        <div className="flex justify-center">
          <Logo size={26} />
        </div>
        <form
          onSubmit={onSubmit}
          className="mt-6 rounded-[var(--radius-card)] border border-line bg-panel p-6 shadow-[var(--shadow-sm)]"
        >
          <h1 className="text-[15px] font-semibold tracking-tight">登录到你的资料库</h1>
          <label className="mt-5 block text-xs text-ink-soft">
            用户名
            <input
              name="username"
              autoComplete="username"
              defaultValue="admin"
              className="mt-1.5 h-9 w-full rounded-[var(--radius-control)] border border-line bg-panel-raised px-3 text-[13px] outline-none focus:border-accent/60"
            />
          </label>
          <label className="mt-3 block text-xs text-ink-soft">
            密码
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              defaultValue="test-password"
              className="mt-1.5 h-9 w-full rounded-[var(--radius-control)] border border-line bg-panel-raised px-3 text-[13px] outline-none focus:border-accent/60"
            />
          </label>
          <button
            type="submit"
            className="mt-5 h-9 w-full rounded-[var(--radius-control)] bg-accent text-[13px] font-medium text-white transition-colors hover:bg-accent-strong"
          >
            登录
          </button>
          <p className="mt-3 text-center text-[11px] text-ink-faint">原型 · 不校验账号</p>
        </form>
      </div>
    </main>
  );
}
