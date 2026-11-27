"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, api, type Habit, type User } from "@/lib/api";
import { localToday, todayLabel } from "@/lib/today";
import { useSlowTask } from "@/lib/useSlowTask";
import { WakingNotice } from "./WakingNotice";
import { HabitRow } from "./HabitRow";
import { Wordmark } from "./Wordmark";

export function HabitsBoard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [habits, setHabits] = useState<Habit[] | null>(null);
  // The local date is only known in the browser (the page itself is prerendered), so it starts empty.
  const [today, setToday] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [adding, setAdding] = useState(false);
  const pending = useRef(new Set<number>()); // habits with a tick request in flight
  const { slow, run } = useSlowTask();

  // Expired or invalid session: clear the cookie, then go to the login page.
  const handleError = useCallback(
    async (e: unknown) => {
      if (e instanceof ApiError && e.status === 401) {
        await api("/auth/logout", { method: "POST" }).catch(() => {});
        router.replace("/login");
        return;
      }
      setError(e instanceof ApiError ? e.message : "Something went wrong. Try again.");
    },
    [router],
  );

  const load = useCallback(
    async (day: string) => {
      try {
        const [me, list] = await run(() => Promise.all([api<User>("/auth/me"), api<Habit[]>(`/habits?today=${day}`)]));
        setUser(me);
        setHabits(list);
      } catch (e) {
        await handleError(e);
      }
    },
    [handleError, run],
  );

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- loading data when the page opens
    if (today) load(today);
  }, [load, today]);

  // Read the local date once in the browser, and again when the tab comes back:
  // left open overnight, the new day starts unticked.
  useEffect(() => {
    const onFocus = () => setToday((current) => (localToday() === current ? current : localToday()));
    onFocus();
    window.addEventListener("focus", onFocus);
    document.addEventListener("visibilitychange", onFocus);
    return () => {
      window.removeEventListener("focus", onFocus);
      document.removeEventListener("visibilitychange", onFocus);
    };
  }, []);

  const update = (id: number, change: Partial<Habit>) =>
    setHabits((list) => list?.map((h) => (h.id === id ? { ...h, ...change } : h)) ?? list);

  async function toggle(habit: Habit) {
    if (!today || pending.current.has(habit.id)) return;
    pending.current.add(habit.id);
    const done = !habit.done_today;
    // Show it right away (optimistic). The streak counts up to yesterday until today is ticked,
    // so ticking today adds one day and unticking removes it.
    update(habit.id, {
      done_today: done,
      streak: habit.streak + (done ? 1 : -1),
      history: done ? [...habit.history, today] : habit.history.filter((day) => day !== today),
    });
    setError(null);
    try {
      await api(`/habits/${habit.id}/check-ins/${today}`, { method: done ? "PUT" : "DELETE" });
    } catch (e) {
      update(habit.id, { done_today: habit.done_today, streak: habit.streak, history: habit.history }); // put it back
      await handleError(e);
    } finally {
      pending.current.delete(habit.id);
    }
  }

  async function add(event: React.FormEvent) {
    event.preventDefault();
    const name = newName.trim();
    if (!name) return;
    setAdding(true);
    setError(null);
    try {
      const habit = await api<Habit>("/habits", { method: "POST", body: { name } });
      setHabits((list) => [...(list ?? []), habit]);
      setNewName("");
    } catch (e) {
      await handleError(e);
    } finally {
      setAdding(false);
    }
  }

  async function rename(habit: Habit, name: string) {
    setError(null);
    try {
      const saved = await api<Habit>(`/habits/${habit.id}?today=${today}`, { method: "PATCH", body: { name } });
      update(habit.id, saved);
      return true;
    } catch (e) {
      await handleError(e);
      return false;
    }
  }

  async function remove(habit: Habit) {
    setError(null);
    try {
      await api(`/habits/${habit.id}`, { method: "DELETE" });
      setHabits((list) => list?.filter((h) => h.id !== habit.id) ?? list);
    } catch (e) {
      await handleError(e);
    }
  }

  async function logout(to = "/") {
    await api("/auth/logout", { method: "POST" }).catch(() => {});
    router.replace(to);
    router.refresh();
  }

  const doneCount = habits?.filter((h) => h.done_today).length ?? 0;
  const total = habits?.length ?? 0;

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col px-5 sm:px-8">
      <header className="flex items-center justify-between gap-4 py-6">
        <Wordmark href="/habits" />
        <div className="flex items-center gap-4 text-sm">
          {user && !user.is_guest && <span className="hidden text-muted sm:inline">{user.email}</span>}
          <button onClick={() => logout()} className="rounded-full border-2 border-line px-4 py-1.5 font-bold transition hover:border-moss">
            Log out
          </button>
        </div>
      </header>

      <main className="flex-1 pb-16 pt-4">
        {user?.is_guest && (
          <div className="mb-6 rounded-2xl border-2 border-moss/30 bg-moss-soft px-4 py-3">
            <p className="font-semibold">You&rsquo;re using a demo account, filled with example habits.</p>
            <p className="mt-0.5 text-sm text-muted">
              Tick, rename or add anything: it&rsquo;s deleted after 24 hours.{" "}
              <button onClick={() => logout("/signup")} className="font-bold text-ink underline decoration-2 underline-offset-4">
                Create your own account
              </button>
            </p>
          </div>
        )}
        <p className="min-h-6 font-semibold text-muted">{today && todayLabel(new Date(`${today}T12:00:00`))}</p>
        <h1 className="mt-1 text-4xl font-extrabold tracking-tight">Today</h1>

        {habits && total > 0 && (
          <div className="mt-5">
            <p className="font-semibold" aria-live="polite">
              {doneCount === total ? "All done for today." : `${doneCount} of ${total} done`}
            </p>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-line" aria-hidden="true">
              <div className="h-full rounded-full bg-moss transition-[width] duration-300" style={{ width: `${(doneCount / total) * 100}%` }} />
            </div>
          </div>
        )}

        <p role="alert" className="mt-4 min-h-6 font-semibold text-danger">
          {error}
        </p>

        {habits === null ? (
          <div className="mt-2">
            <p className="text-muted" aria-live="polite">
              Loading your habits…
            </p>
            <WakingNotice show={slow} />
          </div>
        ) : habits.length === 0 ? (
          <div className="mt-2 rounded-3xl border-2 border-dashed border-line p-8">
            <p className="text-lg font-semibold">No habits yet.</p>
            <p className="mt-1 text-muted">Add the first one below: something small you can do every day.</p>
          </div>
        ) : (
          <ul className="mt-2 space-y-2">
            {habits.map((habit) => (
              <HabitRow key={habit.id} habit={habit} today={today ?? ""} onToggle={toggle} onRename={rename} onDelete={remove} />
            ))}
          </ul>
        )}

        {habits !== null && (
          <form onSubmit={add} className="mt-6 flex gap-2">
            <label className="sr-only" htmlFor="new-habit">
              New habit
            </label>
            <input
              id="new-habit"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              maxLength={60}
              placeholder="New habit, e.g. Stretch 5 minutes"
              className="min-w-0 flex-1 rounded-full border-2 border-line bg-card px-5 py-3 outline-none focus:border-moss"
            />
            <button
              type="submit"
              disabled={adding || !newName.trim()}
              className="shrink-0 rounded-full bg-moss px-5 py-3 font-bold text-on-moss transition hover:brightness-110 disabled:opacity-50"
            >
              {adding ? "Adding…" : "Add habit"}
            </button>
          </form>
        )}
      </main>
    </div>
  );
}
