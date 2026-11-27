import { NextResponse, type NextRequest } from "next/server";

// Only checks whether a session cookie exists, to send people to the right page quickly.
// The API still checks the token on every request: this is a shortcut, not the security.
const SESSION_COOKIE = "session";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const loggedIn = request.cookies.has(SESSION_COOKIE);

  if (pathname.startsWith("/habits") && !loggedIn) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  if ((pathname === "/login" || pathname === "/signup") && loggedIn) {
    return NextResponse.redirect(new URL("/habits", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/habits/:path*", "/login", "/signup"],
};
