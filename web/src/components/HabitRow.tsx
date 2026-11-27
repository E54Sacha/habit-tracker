"use client";

import { useState } from "react";
import type { Habit } from "@/lib/api";
import { Calendar } from "./Calendar";

type Props = {
  habit: Habit;
  today: string;
  onToggle: (habit: Habit) => void;
  onRename: (habit: Habit, name: string) => Promise<boolean>;
  onDelete: (habit: Habit) => void;
};

export function HabitRow({ habit, today, onToggle, onRename, onDelete }: Props) {
  const [mode, setMode] = useState<"view" | "rename" | "confirm-delete">("view");
  const [name, setName] = useState(habit.name);
  const done = habit.done_today;

  async function saveName(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = name.trim();
    if (!trimmed || trimmed === habit.name) {
      setName(habit.name);
      setMode("view");
      return;
    }
    if (await onRename(habit, trimmed)) setMode("view");
  }

  return (
    <li className={`rounded-2xl border px-3 py-3 transition-colors ${done ? "border-transparent bg-moss-soft" : "border-line bg-card"}`}>
      <div className="flex items-center gap-4">
      <button
        type="button"
        onClick={() => onToggle(habit)}
        aria-pressed={done}
        aria-label={`${habit.name}: ${done ? "done today, click to undo" : "mark as done today"}`}
        className={`grid size-11 shrink-0 place-items-center rounded-full border-2 transition active:scale-90 ${done ? "border-moss bg-moss text-on-moss" : "border-line hover:border-moss"}`}
      >
        <svg
          viewBox="0 0 16 16"
          className={`size-5 transition-opacity ${done ? "opacity-100" : "opacity-0"}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M3.5 8.5l3 3 6-7" />
        </svg>
      </button>

      {mode === "rename" ? (
        <form onSubmit={saveName} className="flex min-w-0 flex-1 gap-2">
          <label className="sr-only" htmlFor={`rename-${habit.id}`}>
            New name for {habit.name}
          </label>
          <input
            id={`rename-${habit.id}`}
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Escape") {
                setName(habit.name);
                setMode("view");
              }
            }}
            maxLength={60}
            autoFocus
            className="min-w-0 flex-1 rounded-xl border-2 border-line bg-card px-3 py-1.5 outline-none focus:border-moss"
          />
          <button type="submit" className="rounded-full bg-moss px-4 py-1.5 text-sm font-bold text-on-moss">
            Save
          </button>
        </form>
      ) : (
        <div className="min-w-0 flex-1">
          <span className={`break-words text-lg font-semibold ${done ? "text-muted line-through decoration-2" : ""}`}>{habit.name}</span>
          <p className="text-sm text-muted">{streakLabel(habit)}</p>
        </div>
      )}

      {mode === "view" && (
        // Icons on phones (room for the habit name), words from the sm breakpoint.
        <div className="flex shrink-0 gap-1 text-sm">
          <button type="button" onClick={() => setMode("rename")} className="grid min-h-10 min-w-10 place-items-center rounded-full font-semibold text-muted hover:bg-paper hover:text-ink sm:px-3">
            <svg viewBox="0 0 16 16" className="size-4 sm:hidden" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M10.5 2.5l3 3L5 14H2v-3z" />
            </svg>
            <span className="sr-only sm:not-sr-only">Rename</span>
          </button>
          <button type="button" onClick={() => setMode("confirm-delete")} className="grid min-h-10 min-w-10 place-items-center rounded-full font-semibold text-muted hover:bg-paper hover:text-danger sm:px-3">
            <svg viewBox="0 0 16 16" className="size-4 sm:hidden" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M2.5 4h11M6 4V2.5h4V4M4 4l.7 9.5h6.6L12 4" />
            </svg>
            <span className="sr-only sm:not-sr-only">Delete</span>
          </button>
        </div>
      )}
      {mode === "confirm-delete" && (
        <div className="flex shrink-0 items-center gap-1 text-sm" role="group" aria-label={`Delete ${habit.name}?`}>
          <span className="font-semibold">Delete?</span>
          <button type="button" onClick={() => onDelete(habit)} className="rounded-full bg-danger px-3 py-1.5 font-bold text-paper">
            Yes
          </button>
          <button type="button" onClick={() => setMode("view")} autoFocus className="rounded-full px-3 py-1.5 font-semibold hover:bg-paper">
            No
          </button>
        </div>
      )}
      </div>
      <div className="mt-3 pl-[3.75rem]">
        <Calendar today={today} history={habit.history} />
      </div>
    </li>
  );
}

function streakLabel({ streak, done_today }: Habit): string {
  if (streak === 0) return "No streak yet";
  const days = `${streak} day${streak === 1 ? "" : "s"} in a row`;
  return done_today ? days : `${days}, tick today to keep it`;
}
