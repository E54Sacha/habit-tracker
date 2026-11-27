import Link from "next/link";

export function Wordmark({ href = "/" }: { href?: string }) {
  return (
    <Link href={href} className="inline-flex items-center gap-2 text-xl font-extrabold tracking-tight">
      <span aria-hidden="true" className="grid size-7 place-items-center rounded-full bg-moss text-on-moss">
        <svg viewBox="0 0 16 16" className="size-4" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3.5 8.5l3 3 6-7" />
        </svg>
      </span>
      Steady
    </Link>
  );
}
