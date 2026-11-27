import Link from "next/link";
import { Wordmark } from "@/components/Wordmark";

// A preview of the habit list, so the first screen shows what the app does.
const preview = [
  { name: "Read 10 pages", done: true },
  { name: "Drink 2 litres of water", done: true },
  { name: "Walk 20 minutes", done: false },
];

export default function Home() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-5 sm:px-8">
      <header className="py-6">
        <Wordmark />
      </header>
      <main className="grid flex-1 items-center gap-12 pb-16 md:grid-cols-[1.1fr_1fr] md:gap-16">
        <div>
          <h1 className="max-w-[14ch] text-[clamp(2.5rem,6vw,4rem)] font-extrabold leading-[1.02] tracking-tight">
            Small habits, ticked off every day.
          </h1>
          <p className="mt-5 max-w-[34rem] text-lg leading-relaxed text-muted">
            Add the habits you want to keep, tick them when they&rsquo;re done, and see how many days in a row you&rsquo;ve kept going.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/signup" className="rounded-full bg-moss px-6 py-3 font-bold text-on-moss transition hover:brightness-110">
              Create an account
            </Link>
            <Link href="/login" className="rounded-full border-2 border-line px-6 py-3 font-bold transition hover:border-moss">
              Log in
            </Link>
          </div>
        </div>
        <ul aria-label="Example habits" className="space-y-3 rounded-3xl border border-line bg-card p-5 shadow-sm">
          {preview.map((habit) => (
            <li key={habit.name} className="flex items-center gap-4 rounded-2xl px-2 py-2">
              <span
                aria-hidden="true"
                className={`grid size-10 shrink-0 place-items-center rounded-full border-2 ${habit.done ? "border-moss bg-moss text-on-moss" : "border-line"}`}
              >
                {habit.done && (
                  <svg viewBox="0 0 16 16" className="size-5" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3.5 8.5l3 3 6-7" />
                  </svg>
                )}
              </span>
              <span className={`text-lg font-semibold ${habit.done ? "text-muted line-through decoration-2" : ""}`}>{habit.name}</span>
              <span className="sr-only">{habit.done ? "(done)" : "(not done yet)"}</span>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
