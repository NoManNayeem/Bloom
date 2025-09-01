// src/middleware.js
import { NextResponse } from 'next/server';

export function middleware(req) {
  const { pathname, origin } = req.nextUrl;

  // Public routes that never require auth
  const publicPaths = ['/', '/login', '/register', '/api', '/api-docs'];
  if (publicPaths.some((p) => pathname === p || pathname.startsWith(`${p}/`))) {
    return NextResponse.next();
  }

  // Add your protected routes here
  const protectedMatchers = [/^\/home(\/.*)?$/, /^\/self-analysis(\/.*)?$/];

  const needsAuth = protectedMatchers.some((re) => re.test(pathname));
  if (!needsAuth) return NextResponse.next();

  const access = req.cookies.get('access_token')?.value;

  if (!access) {
    const loginUrl = new URL('/login', origin);
    loginUrl.searchParams.set('next', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

// Match all routes; we'll short-circuit in middleware itself
export const config = {
  matcher: ['/((?!_next|static|favicon.ico|images).*)'],
};
