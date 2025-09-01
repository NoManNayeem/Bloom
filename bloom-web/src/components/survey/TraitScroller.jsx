'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';

function asSortedEntries(obj) {
  if (!obj) return [];
  return Object.entries(obj)
    .map(([k, v]) => [k, Number(v) || 0])
    .sort((a, b) => b[1] - a[1]) // highest first
    .slice(0, 20);               // cap for UI
}

export default function TraitScroller({ positives, negatives }) {
  const pos = useMemo(() => asSortedEntries(positives), [positives]);
  const neg = useMemo(() => asSortedEntries(negatives), [negatives]);

  return (
    <div
      className="rounded-2xl border border-gray-200 bg-white/80 p-4 shadow-sm backdrop-blur will-change-transform"
      aria-label="Trait insights"
    >
      <h3 className="text-sm font-semibold text-gray-900">Traits</h3>

      <div className="mt-3 grid gap-4 md:grid-cols-2">
        {/* Positives */}
        <section aria-label="Positive traits">
          <h4 className="mb-2 text-xs font-medium text-emerald-700">Positives</h4>
          <div className="max-h-64 overflow-y-auto pr-1 md:max-h-72">
            <motion.ul
              initial="hidden"
              animate="show"
              variants={{ hidden: {}, show: { transition: { staggerChildren: 0.05 } } }}
              className="space-y-2"
            >
              {pos.length === 0 && (
                <li className="text-xs text-gray-400">No data yet.</li>
              )}
              {pos.map(([name, val], idx) => (
                <TraitRow key={`pos-${name}-${idx}`} name={name} value={val} positive />
              ))}
            </motion.ul>
          </div>
        </section>

        {/* Negatives */}
        <section aria-label="Growth areas">
          <h4 className="mb-2 text-xs font-medium text-rose-700">Growth Areas</h4>
          <div className="max-h-64 overflow-y-auto pr-1 md:max-h-72">
            <motion.ul
              initial="hidden"
              animate="show"
              variants={{ hidden: {}, show: { transition: { staggerChildren: 0.05 } } }}
              className="space-y-2"
            >
              {neg.length === 0 && (
                <li className="text-xs text-gray-400">No data yet.</li>
              )}
              {neg.map(([name, val], idx) => (
                <TraitRow key={`neg-${name}-${idx}`} name={name} value={val} positive={false} />
              ))}
            </motion.ul>
          </div>
        </section>
      </div>
    </div>
  );
}

function TraitRow({ name, value, positive }) {
  const pct = Math.max(0, Math.min(100, Math.round(value)));
  const gradient = positive
    ? 'from-emerald-500 via-teal-500 to-cyan-500'
    : 'from-rose-500 via-orange-500 to-amber-500';
  const emoji = positive ? '✦' : '⚡';

  return (
    <motion.li
      variants={{
        hidden: { opacity: 0, y: 8, scale: 0.98 },
        show: { opacity: 1, y: 0, scale: 1 },
      }}
      whileHover={{ scale: 1.01 }}
      className="rounded-xl border border-gray-200 bg-white p-3 shadow-sm"
      role="listitem"
      aria-label={`${name}: ${pct}%`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex h-6 w-6 items-center justify-center rounded-lg bg-gradient-to-br ${gradient} text-[11px] text-white`}
            aria-hidden="true"
          >
            {emoji}
          </span>
          <p className="text-sm font-medium text-gray-900">{name}</p>
        </div>
        <p className="text-sm font-semibold text-gray-900">{pct}%</p>
      </div>
      <div className="mt-2 h-2 w-full rounded-full bg-gray-100">
        <div
          className={`h-2 rounded-full bg-gradient-to-r ${gradient}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </motion.li>
  );
}
