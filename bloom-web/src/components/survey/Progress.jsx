'use client';

import { motion } from 'framer-motion';
import FancyProgress from './FancyProgress';

export function ProgressBar({ progress }) {
  const percent = Number(progress?.percent ?? 0) || 0;
  const answered = Number(progress?.answered ?? 0) || 0;
  const total = Number(progress?.total ?? 0) || 0;

  return (
    <div aria-label="Overall progress">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-900">Overall progress</p>
        <p className="text-xs text-gray-600">
          {answered}/{total} ({Math.round(percent)}%)
        </p>
      </div>
      <div className="mt-2">
        <FancyProgress percent={percent} height={8} />
      </div>
    </div>
  );
}

export function ProgressMini({ progress }) {
  if (!progress) return null;
  const percent = Number(progress.percent ?? 0) || 0;
  const answered = Number(progress.answered ?? 0) || 0;
  const total = Number(progress.total ?? 0) || 0;

  return (
    <div aria-label="Compact overall progress">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-700">Overall</span>
        <span className="font-medium text-gray-900">{Math.round(percent)}%</span>
      </div>
      <div className="mt-2">
        <FancyProgress percent={percent} height={6} />
      </div>
      <p className="mt-1 text-xs text-gray-500">
        {answered}/{total} answered
      </p>
    </div>
  );
}

export function CategoryBar({ label, stats }) {
  const percent = Number(stats?.percent ?? 0) || 0;

  return (
    <div aria-label={`${label ?? 'Uncategorized'} progress`}>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-gray-700">{label ?? 'Uncategorized'}</span>
        <span className="text-gray-600">{Math.round(percent)}%</span>
      </div>
      <FancyProgress percent={percent} height={6} />
    </div>
  );
}
