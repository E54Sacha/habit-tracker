"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ApiError, api, wakeServer, type User } from "@/lib/api";
import { localToday } from "@/lib/today";
import { useSlowTask } from "@/lib/useSlowTask";
import { WakingNotice } from "./WakingNotice";

/** The landing page actions: the guest demo first (recruiters won't sign up), then the other links. */
export function GuestButton({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { slow, run } = useSlowTask();

  // Start waking the server while the visitor reads the page.
  useEffect(() => {
    wakeServer().catch(() => {});
  }, []);

  async function tryAsGuest() {
    setBusy(true);
    setError(null);
    try {
      await run(async () => {
        await wakeServer();
        await api<User>("/auth/guest", { method: "POST", body: { today: localToday() } });
      });
      router.replace("/habits");
      router.refresh();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong. Try again.");
      setBusy(false);
    }
  }

  return (
    <div className="mt-8">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={tryAsGuest}
          disabled={busy}
          className="rounded-full bg-moss px-6 py-3 font-bold text-on-moss transition hover:brightness-110 disabled:opacity-60"
        >
          {busy ? "Opening the demo…" : "Try it as a guest"}
        </button>
        {children}
      </div>
      <p className="mt-3 text-sm text-muted">The guest demo needs no sign-up and is deleted after 24 hours.</p>
      <WakingNotice show={slow} />
      {error && (
        <p role="alert" className="font-semibold text-danger">
          {error}
        </p>
      )}
    </div>
  );
}
