'use client';

import { FiBarChart2 } from 'react-icons/fi';
import { ProgressMini, CategoryBar } from './Progress';
import TraitScroller from './TraitScroller';

export default function StatsPanel({ overview }) {
  const byCategory = overview?.progress?.by_category || {};
  const hasCategories = Object.keys(byCategory).length > 0;
  const quote = overview?.self_analysis?.quote;

  return (
    <aside className="space-y-6 lg:sticky lg:top-24">
      {/* Gamified, animated trait scroller */}
      <TraitScroller
        positives={overview?.self_analysis?.combined_positives}
        negatives={overview?.self_analysis?.combined_negatives}
      />

      {/* Optional quote */}
      {quote ? (
        <blockquote className="rounded-2xl border border-indigo-100 bg-indigo-50/60 p-4 text-sm text-indigo-900">
          “{quote}”
        </blockquote>
      ) : null}

      {/* Overview */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50">
            <FiBarChart2 className="h-5 w-5 text-indigo-700" />
          </div>
          <h2 className="text-sm font-semibold text-gray-900">Overview</h2>
        </div>

        <ProgressMini progress={overview?.progress} />

        <div className="mt-5 space-y-3">
          <p className="text-xs font-medium text-gray-500">By category</p>
          <div className="space-y-2">
            {hasCategories ? (
              Object.entries(byCategory).map(([cat, stats]) => (
                <CategoryBar
                  key={cat || 'uncategorized'}
                  label={cat || 'Uncategorized'}
                  stats={stats}
                />
              ))
            ) : (
              <p className="text-xs text-gray-500">No categories yet.</p>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
