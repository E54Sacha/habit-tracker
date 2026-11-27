// "Today" is the user's local day, not UTC: a habit done at 23:30 in Paris counts for that day.

const pad = (n: number) => String(n).padStart(2, "0");

/** The local date as YYYY-MM-DD, the format the API expects. */
export function localToday(now = new Date()): string {
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

/** "Thursday 27 November" */
export function todayLabel(now = new Date()): string {
  return now.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" });
}

/** YYYY-MM-DD plus n days (n can be negative), in local time. */
export function addDays(day: string, n: number): string {
  const d = new Date(`${day}T12:00:00`); // noon: daylight saving changes can't push it to another day
  d.setDate(d.getDate() + n);
  return localToday(d);
}

/** 0 = Monday … 6 = Sunday */
export function weekdayIndex(day: string): number {
  return (new Date(`${day}T12:00:00`).getDay() + 6) % 7;
}
