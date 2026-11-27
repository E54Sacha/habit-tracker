// Calls to the FastAPI server. Always through /api/* on this site (see next.config.ts rewrites).

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

type Options = { method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE"; body?: unknown };

// The free API server sleeps after 15 minutes without visitors and takes up to a minute to start.
// wakeServer() asks /health until it answers; everyone waits on the same attempt.
let waking: Promise<void> | null = null;

export function wakeServer(): Promise<void> {
  waking ??= (async () => {
    const deadline = Date.now() + 120_000;
    for (;;) {
      try {
        if ((await fetch("/api/health", { cache: "no-store" })).ok) return;
      } catch {
        // not reachable yet: try again
      }
      if (Date.now() > deadline) {
        waking = null;
        throw new ApiError(0, "The server didn't wake up. Try again in a minute.");
      }
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
  })();
  return waking;
}

const SAFE_TO_RETRY = new Set(["GET", "PUT", "DELETE"]); // repeating them changes nothing

export async function api<T = void>(path: string, options: Options = {}): Promise<T> {
  try {
    return await request<T>(path, options);
  } catch (e) {
    // 502/503/504: the server fell asleep again. Wake it, then retry once if that's safe.
    if (e instanceof ApiError && [502, 503, 504].includes(e.status) && SAFE_TO_RETRY.has(options.method ?? "GET")) {
      waking = null;
      await wakeServer();
      return request<T>(path, options);
    }
    throw e;
  }
}

async function request<T>(path: string, { method = "GET", body }: Options): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method,
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: "same-origin",
      cache: "no-store",
    });
  } catch {
    throw new ApiError(0, "Can't reach the server. Check your connection and try again.");
  }
  if (response.status === 204) return undefined as T;

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    // FastAPI sends {"detail": "message"} for our own errors, and a list for validation errors.
    const detail = typeof data?.detail === "string" ? data.detail : null;
    const fallback = response.status >= 500 ? "The server had a problem. Try again in a moment." : "Please check what you entered.";
    throw new ApiError(response.status, detail ?? fallback);
  }
  return data as T;
}

export type User = { id: number; email: string; is_guest: boolean };
/** history: ticked days of the last 8 weeks (YYYY-MM-DD), oldest first */
export type Habit = { id: number; name: string; done_today: boolean; streak: number; history: string[] };
