'use client';

import { motion } from 'framer-motion';
import clsx from 'clsx';

/**
 * FancyProgress
 * - Animated, glossy progress bar with gradient fill
 * - Accessible ARIA progressbar semantics
 *
 * Props:
 *  - percent: number (0..100)
 *  - height: number (px)
 *  - showLabel: boolean (renders % text)
 *  - label: string (aria-label override)
 *  - className: string (extra wrapper classes)
 */
export default function FancyProgress({
  percent = 0,
  height = 10,
  showLabel = false,
  label = 'Progress',
  className,
}) {
  const clamped = Math.max(0, Math.min(100, Number(percent) || 0));

  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(clamped)}
      className={clsx(
        'relative w-full overflow-hidden rounded-full bg-gray-100',
        className
      )}
      style={{ height }}
    >
      {/* Fill */}
      <motion.div
        className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-pink-500"
        initial={{ width: 0 }}
        animate={{ width: `${clamped}%` }}
        transition={{ type: 'spring', stiffness: 60, damping: 20 }}
      />

      {/* Shine */}
      <div className="pointer-events-none absolute inset-0 opacity-30 mix-blend-overlay">
        <div className="h-full w-full bg-[linear-gradient(60deg,rgba(255,255,255,.55)_0%,rgba(255,255,255,0)_40%)] animate-[shine_2.4s_ease-in-out_infinite]" />
      </div>

      {/* Optional label */}
      {showLabel && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-medium text-gray-800 drop-shadow-sm">
            {Math.round(clamped)}%
          </span>
        </div>
      )}

      {/* Keyframes */}
      <style jsx global>{`
        @keyframes shine {
          0% {
            transform: translateX(-100%);
          }
          50% {
            transform: translateX(0%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
}
