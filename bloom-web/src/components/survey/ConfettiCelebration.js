'use client';

import confetti from 'canvas-confetti';

/**
 * Lightweight confetti helper for celebratory moments.
 * - Respects prefers-reduced-motion.
 * - Safe no-op on SSR.
 *
 * @param {Object} opts
 * @param {number} [opts.scalar=1]          Size multiplier for particles
 * @param {number} [opts.spread=70]         Spread angle of particles
 * @param {number} [opts.particleCount=100] Number of particles
 * @param {Object} [opts.origin]            {x, y} origin (0..1). Default y=0.6
 * @param {string[]} [opts.colors]          Array of hex colors
 */
export function blastConfetti({
  scalar = 1,
  spread = 70,
  particleCount = 100,
  origin,
  colors,
} = {}) {
  // SSR guard
  if (typeof window === 'undefined') return;

  // Respect reduced motion
  const prefersReduced =
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) return;

  const defaults = {
    origin: origin ?? { y: 0.6 },
    scalar,
    colors,
    // Let the library also avoid heavy effects if user prefers reduced motion
    disableForReducedMotion: true,
  };

  // First burst
  confetti({
    ...defaults,
    spread,
    particleCount,
    ticks: 120,
  });

  // Follow-up burst with slight variation
  setTimeout(() => {
    confetti({
      ...defaults,
      origin: { x: Math.random() * 0.4 + 0.3, y: defaults.origin.y },
      spread: spread + 18,
      particleCount: Math.round(particleCount * 0.6),
      ticks: 110,
    });
  }, 120);
}
