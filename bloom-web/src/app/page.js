'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiShield, FiZap, FiBarChart2 } from 'react-icons/fi';

const fade = {
  hidden: { opacity: 0, y: 10 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.05 * i, type: 'spring', stiffness: 120, damping: 16 },
  }),
};

export default function Page() {
  return (
    <main className="relative min-h-[calc(100svh-64px)] overflow-hidden bg-gradient-to-b from-white to-indigo-50">
      <AnimatedBg />

      {/* Hero (compact) */}
      <section className="relative mx-auto max-w-6xl px-4 pt-12 sm:px-6 lg:px-8">
        <div className="grid items-center gap-10 md:grid-cols-2">
          <div>
            <motion.span
              className="inline-flex items-center rounded-full bg-indigo-100 px-3 py-1 text-[11px] font-medium text-indigo-700"
              variants={fade}
              initial="hidden"
              animate="show"
            >
              New • Self-Analysis Survey
            </motion.span>

            <motion.h1
              className="mt-3 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl"
              variants={fade}
              custom={1}
              initial="hidden"
              animate="show"
            >
              Turn honest answers into{' '}
              <span className="bg-gradient-to-r from-indigo-600 via-fuchsia-600 to-pink-600 bg-clip-text text-transparent">
                actionable insights
              </span>
              .
            </motion.h1>

            <motion.p
              className="mt-3 text-base leading-7 text-gray-600"
              variants={fade}
              custom={2}
              initial="hidden"
              animate="show"
            >
              Answer one question at a time, track progress by category, and see your strengths
              and growth areas come to life.
            </motion.p>

            <motion.div
              className="mt-6 flex flex-wrap items-center gap-3"
              variants={fade}
              custom={3}
              initial="hidden"
              animate="show"
            >
              <Link
                href="/register"
                className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-indigo-700"
              >
                Get Started
              </Link>
              <Link
                href="/login"
                className="rounded-xl border border-gray-300 bg-white px-5 py-2.5 text-sm font-semibold text-gray-700 transition hover:-translate-y-0.5 hover:bg-gray-50"
              >
                I already have an account
              </Link>
            </motion.div>

            {/* Tiny trust strip (compact, not a features section) */}
            <motion.div
              className="mt-5 flex flex-wrap items-center gap-4 text-[12px] text-gray-600"
              variants={fade}
              custom={4}
              initial="hidden"
              animate="show"
            >
              <Badge icon={<FiZap />} text="One-at-a-time flow" />
              <Badge icon={<FiBarChart2 />} text="Live stats" />
              <Badge icon={<FiShield />} text="Secure & private" />
            </motion.div>
          </div>

          {/* Preview card */}
          <motion.div className="relative" variants={fade} custom={5} initial="hidden" animate="show">
            <div className="mx-auto w-full max-w-md rounded-3xl border border-gray-200 bg-white/80 p-5 shadow-lg backdrop-blur">
              {/* window dots */}
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-red-400" />
                <div className="h-2 w-2 rounded-full bg-yellow-400" />
                <div className="h-2 w-2 rounded-full bg-green-400" />
              </div>

              {/* mini HUD */}
              <div className="mt-4 grid grid-cols-3 gap-2">
                <HudChip label="Level" value="1" />
                <HudChip label="Answered" value="0/6" />
                <HudChip label="XP" value="0" />
              </div>

              {/* sample question */}
              <div className="mt-4 space-y-3">
                <p className="text-sm font-medium text-gray-900">Example Question</p>
                <div className="rounded-2xl border border-gray-200 p-4">
                  <p className="text-sm text-gray-700">Tell us a childhood memory you are proud of.</p>
                </div>
                <div className="flex items-center gap-3">
                  <button className="flex-1 rounded-xl bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition hover:-translate-y-0.5 hover:bg-gray-200">
                    Skip
                  </button>
                  <button className="flex-1 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:-translate-y-0.5 hover:bg-indigo-700">
                    Answer
                  </button>
                </div>

                {/* animated progress */}
                <div>
                  <AnimatedProgress percent={20} />
                  <p className="mt-1 text-xs text-gray-500">Progress · 20%</p>
                </div>
              </div>
            </div>

            {/* soft glow */}
            <div className="pointer-events-none absolute -inset-8 -z-10 rounded-[2rem] bg-indigo-300/20 blur-3xl" />
          </motion.div>
        </div>
      </section>

      {/* Compact CTA */}
      <section className="mx-auto my-14 max-w-6xl px-4 sm:px-6 lg:px-8">
        <motion.div
          className="relative rounded-2xl bg-indigo-600 px-5 py-8 text-center text-white sm:px-10"
          variants={fade}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-80px' }}
        >
          <div className="pointer-events-none absolute inset-0 rounded-2xl ring-1 ring-white/20">
            <div className="absolute inset-0 rounded-2xl opacity-20 [background:radial-gradient(550px_circle_at_50%_-20%,#fff,transparent_60%)]" />
          </div>

          <h2 className="text-lg font-semibold">Ready to discover your patterns?</h2>
          <p className="mx-auto mt-1 max-w-xl text-[13px] text-indigo-100">
            Create your account and start answering in minutes.
          </p>

          <div className="mt-5 flex justify-center gap-3">
            <Link
              href="/register"
              className="rounded-xl bg-white px-5 py-2.5 text-sm font-semibold text-indigo-700 shadow-sm transition hover:-translate-y-0.5 hover:bg-gray-100"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="rounded-xl border border-white/60 px-5 py-2.5 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-white/10"
            >
              Sign In
            </Link>
          </div>
        </motion.div>
      </section>
    </main>
  );
}

/* ---------- bits ---------- */

function Badge({ icon, text }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white/80 px-3 py-1 backdrop-blur">
      <span className="text-indigo-700">{icon}</span>
      <span>{text}</span>
    </span>
  );
}

function HudChip({ label, value }) {
  return (
    <div className="rounded-xl bg-gray-50 p-2.5 text-center">
      <p className="text-[10px] text-gray-500">{label}</p>
      <p className="text-sm font-semibold text-gray-900">{value}</p>
    </div>
  );
}

function AnimatedProgress({ percent = 0 }) {
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <div className="relative h-2 w-full overflow-hidden rounded-full bg-gray-100">
      <motion.div
        className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-pink-500"
        initial={{ width: 0 }}
        animate={{ width: `${clamped}%` }}
        transition={{ type: 'spring', stiffness: 80, damping: 20 }}
      />
      <div className="pointer-events-none absolute inset-0 opacity-30 mix-blend-overlay">
        <div className="h-full w-full bg-[linear-gradient(60deg,rgba(255,255,255,.5)_0%,rgba(255,255,255,0)_40%)] animate-[shine_2.2s_ease-in-out_infinite]" />
      </div>
      <style jsx global>{`
        @keyframes shine {
          0% { transform: translateX(-100%); }
          50% { transform: translateX(0%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}

function AnimatedBg() {
  return (
    <>
      {/* top-right blob */}
      <motion.div
        className="pointer-events-none absolute -top-24 right-[-10%] h-[24rem] w-[24rem] rounded-full bg-indigo-300/25 blur-3xl"
        initial={{ opacity: 0.5, scale: 0.9 }}
        animate={{ opacity: 0.7, scale: 1 }}
        transition={{ duration: 2.4, repeat: Infinity, repeatType: 'mirror' }}
      />
      {/* mid-left blob */}
      <motion.div
        className="pointer-events-none absolute left-[-10%] top-1/3 h-[18rem] w-[18rem] rounded-full bg-fuchsia-300/25 blur-3xl"
        initial={{ opacity: 0.4, scale: 1 }}
        animate={{ opacity: 0.6, scale: 1.05 }}
        transition={{ duration: 2.8, repeat: Infinity, repeatType: 'mirror' }}
      />
    </>
  );
}
