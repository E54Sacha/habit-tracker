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

export async function api<T = void>(path: string, { method = "GET", body }: Options = {}): Promise<T> {
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

export type User = { id: number; email: string };
export type Habit = { id: number; name: string; done_today: boolean };
