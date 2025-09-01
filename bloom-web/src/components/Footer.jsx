'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

const fade = {
  hidden: { opacity: 0, y: 6 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 120, damping: 18 } },
};

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-16 border-t border-gray-200/70 bg-white/70 backdrop-blur">
      <motion.div
        className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8"
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: '-80px' }}
        variants={fade}
      >
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-indigo-600 to-fuchsia-600" />
              <span className="pointer-events-none absolute inset-0 -z-10 rounded-xl bg-indigo-300/20 blur-lg" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900">Bloom — Self Analysis</p>
              <p className="text-xs text-gray-600">
                A compact, gamified self-analysis survey for actionable insight.
              </p>
            </div>
          </div>

          {/* Quick links */}
          <nav className="flex flex-wrap items-center gap-4 text-sm">
            <FooterLink href="/">Home</FooterLink>
            <FooterLink href="/home">Survey</FooterLink>
            <FooterLink href="/login">Login</FooterLink>
            <FooterLink href="/register">Register</FooterLink>
          </nav>
        </div>

        {/* Bottom line */}
        <div className="mt-6 flex items-center justify-between border-t border-gray-200 pt-4">
          <p className="text-xs text-gray-500">© {year} Bloom. All rights reserved.</p>
          <p className="text-xs text-gray-400">Built with Next.js & DRF</p>
        </div>
      </motion.div>
    </footer>
  );
}

function FooterLink({ href, children }) {
  return (
    <Link
      href={href}
      className="text-gray-600 transition hover:-translate-y-0.5 hover:text-gray-900"
    >
      {children}
    </Link>
  );
}
