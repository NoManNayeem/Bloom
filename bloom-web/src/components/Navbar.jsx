'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import { FiMenu, FiX, FiLogOut } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';

/* ---------- cookie helpers ---------- */
function getCookie(name) {
  if (typeof document === 'undefined') return null;
  const m = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return m ? decodeURIComponent(m[2]) : null;
}

function setCookie(name, value, opts = {}) {
  const { maxAge, path = '/', sameSite = 'Lax' } = opts;
  const secure =
    typeof window !== 'undefined' && window.location.protocol === 'https:' ? '; Secure' : '';
  const maxAgeStr = typeof maxAge === 'number' ? `; Max-Age=${maxAge}` : '';
  document.cookie = `${name}=${encodeURIComponent(
    value
  )}; Path=${path}${maxAgeStr}; SameSite=${sameSite}${secure}`;
}

function deleteCookie(name) {
  setCookie(name, '', { maxAge: 0 });
}

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [authed, setAuthed] = useState(false);
  const [username, setUsername] = useState('');
  const pathname = usePathname();
  const router = useRouter();

  // Re-read cookies on route changes (and on mount)
  useEffect(() => {
    const access = getCookie('access_token');
    const uname = getCookie('username') || '';
    setAuthed(!!access);
    setUsername(uname);
  }, [pathname]);

  const isActive = (href) => (href === '/' ? pathname === '/' : pathname.startsWith(href));

  const desktopNav = useMemo(() => {
    if (authed) {
      return [{ href: '/home', label: 'Home' }];
    }
    return [
      { href: '/login', label: 'Login' },
      { href: '/register', label: 'Register' },
    ];
  }, [authed]);

  const handleLogout = () => {
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    deleteCookie('username');
    setAuthed(false);
    setUsername('');
    router.replace('/login');
  };

  // Initials pill for username
  const initials = (username || '')
    .split(' ')
    .map((s) => s[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200/70 bg-white/70 backdrop-blur">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Brand */}
        <Link href="/" className="group flex items-center gap-2">
          <div className="relative">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-indigo-600 to-fuchsia-600" />
            {/* subtle glow */}
            <span className="pointer-events-none absolute inset-0 -z-10 rounded-xl bg-indigo-300/20 blur-lg opacity-0 transition-opacity group-hover:opacity-100" />
          </div>
          <span className="font-semibold tracking-tight">
            Bloom - <span className="text-gray-900">Self Analysis</span>
          </span>
        </Link>

        {/* Desktop */}
        <div className="hidden items-center gap-6 md:flex">
          <div className="relative flex items-center gap-2">
            {desktopNav.map((item) => (
              <NavItem key={item.href} href={item.href} active={isActive(item.href)}>
                {item.label}
              </NavItem>
            ))}
          </div>

          {/* Right side: CTA or user chip + logout */}
          {authed ? (
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700">
                <span className="relative flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-indigo-600 to-fuchsia-600 text-[11px] font-semibold text-white">
                  {initials || 'U'}
                  {/* tiny ring */}
                  <span className="absolute inset-0 rounded-full ring-2 ring-indigo-200/50" />
                </span>
                <span className="max-w-[10rem] truncate">{username || 'Account'}</span>
              </span>
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-2 rounded-xl border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 shadow-sm transition hover:-translate-y-0.5 hover:bg-gray-50"
              >
                <FiLogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
          ) : (
            <Link
              href="/register"
              className="rounded-xl border border-indigo-600 bg-white px-4 py-2 text-sm font-medium text-indigo-700 shadow-sm transition hover:-translate-y-0.5 hover:bg-indigo-50"
            >
              Get Started
            </Link>
          )}
        </div>

        {/* Mobile toggle */}
        <button
          aria-label="Toggle Navigation"
          onClick={() => setOpen((s) => !s)}
          className="inline-flex items-center justify-center rounded-lg p-2 text-gray-700 hover:bg-gray-100 md:hidden"
        >
          {open ? <FiX className="h-6 w-6" /> : <FiMenu className="h-6 w-6" />}
        </button>
      </nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {open && (
          <motion.div
            key="mobile-menu"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2 }}
            className="border-t border-gray-200 bg-white md:hidden"
          >
            <div className="mx-auto max-w-7xl px-4 py-3">
              <div className="flex flex-col gap-2">
                {desktopNav.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className={`rounded-lg px-3 py-2 text-sm ${
                      isActive(item.href)
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {item.label}
                  </Link>
                ))}

                {authed ? (
                  <>
                    <div className="mt-1 flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2">
                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-indigo-600 to-fuchsia-600 text-xs font-semibold text-white">
                        {initials || 'U'}
                      </span>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-gray-900">
                          {username || 'Account'}
                        </p>
                        <p className="text-xs text-gray-500">Signed in</p>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setOpen(false);
                        handleLogout();
                      }}
                      className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm hover:bg-gray-50"
                    >
                      <FiLogOut className="h-4 w-4" />
                      Logout
                    </button>
                  </>
                ) : (
                  <Link
                    href="/register"
                    onClick={() => setOpen(false)}
                    className="rounded-lg bg-gradient-to-r from-indigo-600 to-fuchsia-600 px-3 py-2 text-center text-sm font-medium text-white shadow-sm hover:opacity-95"
                  >
                    Get Started
                  </Link>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

/* ---------- bits ---------- */

function NavItem({ href, children, active }) {
  return (
    <Link
      href={href}
      className={`relative rounded-lg px-2.5 py-1.5 text-sm transition ${
        active ? 'text-indigo-700' : 'text-gray-600 hover:text-gray-900'
      }`}
    >
      <span className="relative z-10">{children}</span>
      {/* animated underline */}
      <AnimatePresence initial={false}>
        {active && (
          <motion.span
            layoutId="nav-underline"
            className="absolute inset-x-1 bottom-0 h-0.5 rounded-full bg-gradient-to-r from-indigo-600 via-fuchsia-600 to-pink-600"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        )}
      </AnimatePresence>
    </Link>
  );
}
