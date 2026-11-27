export function WakingNotice({ show }: { show: boolean }) {
  return (
    <p aria-live="polite" className="min-h-6 text-sm font-semibold text-muted">
      {show && "Waking up the server. The free plan sleeps when nobody visits; this can take up to a minute…"}
    </p>
  );
}
