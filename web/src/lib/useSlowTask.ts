"use client";

import { useCallback, useRef, useState } from "react";

/** Runs an async task and turns on `slow` if it takes more than 3 seconds (the server is waking up). */
export function useSlowTask() {
  const [slow, setSlow] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const run = useCallback(async <T,>(task: () => Promise<T>): Promise<T> => {
    timer.current = setTimeout(() => setSlow(true), 3000);
    try {
      return await task();
    } finally {
      if (timer.current) clearTimeout(timer.current);
      setSlow(false);
    }
  }, []);

  return { slow, run };
}
