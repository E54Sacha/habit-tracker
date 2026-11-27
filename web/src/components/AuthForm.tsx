"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ApiError, api, wakeServer, type User } from "@/lib/api";
import { useSlowTask } from "@/lib/useSlowTask";
import { WakingNotice } from "./WakingNotice";

type Mode = "signup" | "login";

const text = {
  signup: {
    title: "Create your account",
    submit: "Create account",
    busy: "Creating your account…",
    switch: "Already have an account?",
    switchLink: "Log in",
    switchHref: "/login",
  },
  login: {
    title: "Log in",
    submit: "Log in",
    busy: "Logging in…",
    switch: "New here?",
    switchLink: "Create an account",
    switchHref: "/signup",
  },
};

export function AuthForm({ mode }: { mode: Mode }) {
  const t = text[mode];
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const { slow, run } = useSlowTask();

  useEffect(() => {
    wakeServer().catch(() => {}); // wake the server while the visitor types
  }, []);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      await run(async () => {
        await wakeServer();
        await api<User>(`/auth/${mode}`, {
          method: "POST",
          body: { email: form.get("email"), password: form.get("password") },
        });
      });
      router.replace("/habits");
      router.refresh();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong. Try again.");
      setBusy(false);
    }
  }

  return (
    <div className="w-full max-w-sm">
      <h1 className="text-3xl font-extrabold tracking-tight">{t.title}</h1>
      <form onSubmit={onSubmit} className="mt-8 space-y-5">
        <label className="block">
          <span className="font-semibold">Email</span>
          <input
            name="email"
            type="email"
            required
            maxLength={254}
            autoComplete="email"
            className="mt-1.5 w-full rounded-xl border-2 border-line bg-card px-4 py-3 outline-none focus:border-moss"
          />
        </label>
        <label className="block">
          <span className="font-semibold">Password</span>
          <input
            name="password"
            type="password"
            required
            minLength={mode === "signup" ? 8 : 1}
            maxLength={128}
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
            aria-describedby={mode === "signup" ? "password-hint" : undefined}
            className="mt-1.5 w-full rounded-xl border-2 border-line bg-card px-4 py-3 outline-none focus:border-moss"
          />
          {mode === "signup" && (
            <span id="password-hint" className="mt-1.5 block text-sm text-muted">
              At least 8 characters.
            </span>
          )}
        </label>
        <p role="alert" className="min-h-6 font-semibold text-danger">
          {error}
        </p>
        <WakingNotice show={slow} />
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-full bg-moss px-6 py-3 font-bold text-on-moss transition hover:brightness-110 disabled:opacity-60"
        >
          {busy ? t.busy : t.submit}
        </button>
      </form>
      <p className="mt-6 text-muted">
        {t.switch}{" "}
        <Link href={t.switchHref} className="font-bold text-ink underline decoration-2 underline-offset-4">
          {t.switchLink}
        </Link>
      </p>
    </div>
  );
}
