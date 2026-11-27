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
