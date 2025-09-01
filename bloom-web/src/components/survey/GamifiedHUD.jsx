'use client';

import { motion } from 'framer-motion';
import FancyProgress from './FancyProgress';

function computeLevel(xp) {
  const base = 120; // xp per level
  const level = Math.floor(xp / base) + 1;
  const current = xp % base;
  const toNext = base - current;
  const pct = Math.round((current / base) * 100);
  return { level, current, toNext, pct, base };
}

export default function GamifiedHUD({ answered = 0, percent = 0, xp = 0 }) {
  const { level, pct, current, toNext } = computeLevel(xp);

  return (
    <motion.div
      className="rounded-xl border border-indigo-100 bg-white/80 p-3 shadow-sm backdrop-blur"
      initial={{ y: -8, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 120, damping: 14 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[11px] text-indigo-600">Level</p>
          <p className="text-lg font-bold leading-tight">{level}</p>
        </div>
        <div className="text-right">
          <p className="text-[11px] text-pink-600">XP</p>
          <p className="text-lg font-bold leading-tight">{xp}</p>
        </div>
      </div>

      <div className="mt-2">
        <FancyProgress percent={pct} height={8} />
        <p className="mt-1 text-[10px] text-gray-600">
          {current} XP · {toNext} to next
        </p>
      </div>

      <div className="mt-2 grid grid-cols-3 gap-2 text-center">
        <HUDChip label="Answered" value={answered} />
        <HUDChip label="Progress" value={`${percent}%`} />
        <HUDChip label="Level" value={level} />
      </div>
    </motion.div>
  );
}

function HUDChip({ label, value }) {
  return (
    <div className="rounded-lg bg-gray-50 px-2 py-1.5">
      <p className="text-[10px] text-gray-500">{label}</p>
      <p className="text-sm font-semibold text-gray-900">{value}</p>
    </div>
  );
}
