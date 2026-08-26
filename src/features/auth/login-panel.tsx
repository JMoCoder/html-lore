"use client";

import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { BrandMark } from "@/components/ui/brand-mark";
import { Button } from "@/components/ui/button";

export function LoginPanel() {
  const router = useRouter();

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    router.push("/");
  }

  return (
    <main className="flex min-h-dvh items-center justify-center px-5">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-[380px] rounded-3xl border border-line bg-card p-8 shadow-[var(--shadow)]"
      >
        <BrandMark />
        <p className="mt-5 text-sm leading-relaxed text-ink-soft">
          自托管 HTML 知识工作台。这一版只做阅读、筛选、修改和分享。
        </p>
        <label className="mt-7 block text-xs tracking-wide text-ink-faint">
          用户名
          <input
            name="username"
            defaultValue="admin"
            autoComplete="username"
            className="mt-1.5 h-10 w-full rounded-xl border border-line bg-paper px-3 text-sm text-ink outline-none focus:border-accent"
          />
        </label>
        <label className="mt-4 block text-xs tracking-wide text-ink-faint">
          密码
          <input
            name="password"
            type="password"
            defaultValue="test-password"
            autoComplete="current-password"
            className="mt-1.5 h-10 w-full rounded-xl border border-line bg-paper px-3 text-sm text-ink outline-none focus:border-accent"
          />
        </label>
        <Button type="submit" className="mt-6 w-full">
          进入工作台
        </Button>
        <p className="mt-4 text-center text-[11px] text-ink-faint">原型：不会校验账号</p>
      </form>
    </main>
  );
}
