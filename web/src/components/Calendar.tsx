import { addDays, weekdayIndex } from "@/lib/today";

const WEEKS = 8;
const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

/** The last 8 weeks as small squares, one column per week (Monday at the top), like GitHub's contributions. */
export function Calendar({ today, history }: { today: string; history: string[] }) {
  const done = new Set(history);
  const firstMonday = addDays(today, -weekdayIndex(today) - 7 * (WEEKS - 1));
  const days = Array.from({ length: WEEKS * 7 }, (_, i) => addDays(firstMonday, i));
  const count = days.filter((day) => day <= today && done.has(day)).length;

  return (
    <div
      role="img"
      aria-label={`Done on ${count} of the days shown in the last ${WEEKS} weeks`}
      className="grid w-max grid-flow-col grid-rows-7 gap-[3px]"
    >
      {days.map((day) =>
        day > today ? (
          <span key={day} className="size-2.5" />
        ) : (
          <span
            key={day}
            title={`${DAY_NAMES[weekdayIndex(day)]} ${day}${done.has(day) ? ": done" : ""}`}
            className={`size-2.5 rounded-[3px] ${done.has(day) ? "bg-moss" : "bg-line"} ${day === today ? "ring-2 ring-moss/40 ring-offset-1 ring-offset-card" : ""}`}
          />
        ),
      )}
    </div>
  );
}
