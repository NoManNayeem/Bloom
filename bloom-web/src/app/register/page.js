'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { FiUser, FiLock, FiUserPlus, FiAlertCircle } from 'react-icons/fi';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const fade = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 120, damping: 16 } },
};

export default function RegisterPage() {
  const router = useRouter();
  const params = useSearchParams();
  const nextUrl = params?.get('next') || '/home';

  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState('');

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((s) => ({ ...s, [name]: value }));
  };

  const setCookie = (name, value, maxAgeSeconds) => {
    const secure =
      typeof window !== 'undefined' && window.location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = `${name}=${encodeURIComponent(
      value
    )}; Path=/; Max-Age=${maxAgeSeconds}; SameSite=Lax${secure}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/accounts/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const msg =
          data?.detail ||
          (Array.isArray(data?.username) ? data.username.join(', ') : '') ||
          'Registration failed.';
        throw new Error(msg);
      }

      // data: { id, username, refresh, access }
      const access  = data.access;
      const refresh = data.refresh;
      if (!access) throw new Error('No access token returned by API.');

      // Store tokens (match SIMPLE_JWT defaults: 30m / 7d)
      setCookie('access_token', access, 60 * 30);
      if (refresh) setCookie('refresh_token', refresh, 60 * 60 * 24 * 7);
      setCookie('username', data.username || form.username, 60 * 60 * 24 * 7);

      router.replace(nextUrl);
    } catch (err) {
      setError(err.message || 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-[calc(100svh-64px)] overflow-hidden bg-gradient-to-b from-white to-indigo-50">
      <AnimatedBg />

      <div className="mx-auto flex w-full max-w-7xl items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
        <motion.div
          className="w-full max-w-md rounded-2xl border border-gray-200 bg-white/80 p-6 shadow-sm backdrop-blur"
          variants={fade}
          initial="hidden"
          animate="show"
        >
          <div className="mb-6 text-center">
            <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-fuchsia-600 text-white shadow-sm">
              <FiUserPlus className="h-5 w-5" />
            </div>
            <h1 className="text-xl font-semibold text-gray-900">Create your account</h1>
            <p className="mt-1 text-sm text-gray-600">Sign up to start your self-analysis journey.</p>
          </div>

          {error && (
            <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              <FiAlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <label className="block">
              <span className="mb-1 flex items-center gap-2 text-sm font-medium text-gray-700">
                <FiUser className="h-4 w-4" />
                Username
              </span>
              <input
                type="text"
                name="username"
                value={form.username}
                onChange={onChange}
                autoComplete="username"
                required
                className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
                placeholder="e.g. johndoe"
              />
            </label>

            <label className="block">
              <span className="mb-1 flex items-center gap-2 text-sm font-medium text-gray-700">
                <FiLock className="h-4 w-4" />
                Password
              </span>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={onChange}
                autoComplete="new-password"
                minLength={6}
                required
                className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
                placeholder="At least 6 characters"
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-indigo-700 disabled:opacity-60"
            >
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-indigo-700 hover:underline">
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </main>
  );
}

/* ---------- Animated BG ---------- */
function AnimatedBg() {
  return (
    <>
      <motion.div
        className="pointer-events-none absolute -top-24 right-[-10%] h-[22rem] w-[22rem] rounded-full bg-indigo-300/25 blur-3xl"
        initial={{ opacity: 0.45, scale: 0.92 }}
        animate={{ opacity: 0.65, scale: 1 }}
        transition={{ duration: 2.4, repeat: Infinity, repeatType: 'mirror' }}
      />
      <motion.div
        className="pointer-events-none absolute left-[-10%] top-1/3 h-[18rem] w-[18rem] rounded-full bg-fuchsia-300/25 blur-3xl"
        initial={{ opacity: 0.35, scale: 1 }}
        animate={{ opacity: 0.55, scale: 1.05 }}
        transition={{ duration: 2.8, repeat: Infinity, repeatType: 'mirror' }}
      />
    </>
  );
}
