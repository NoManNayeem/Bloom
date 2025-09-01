'use client';

export function HomeSkeleton() {
  return (
    <div className="grid gap-6 lg:grid-cols-12">
      {/* Main column skeleton */}
      <div className="lg:col-span-7 xl:col-span-8">
        <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
          {/* Header row */}
          <div className="flex items-center justify-between">
            <div className="h-5 w-40 animate-pulse rounded bg-gray-200" />
            <div className="h-6 w-28 animate-pulse rounded-full bg-gray-200" />
          </div>

          {/* Progress */}
          <div className="mt-4 h-2 w-full animate-pulse rounded-full bg-gray-100" />

          {/* Question block */}
          <div className="mt-6 space-y-3">
            <div className="h-4 w-3/4 animate-pulse rounded bg-gray-200" />
            <div className="h-4 w-2/3 animate-pulse rounded bg-gray-200" />
            <div className="mt-3 h-28 w-full animate-pulse rounded-2xl bg-gray-100" />
          </div>

          {/* Actions */}
          <div className="mt-5 flex items-center justify-end gap-3">
            <div className="h-9 w-24 animate-pulse rounded-xl bg-gray-200" />
            <div className="h-9 w-28 animate-pulse rounded-xl bg-gray-300" />
          </div>
        </div>
      </div>

      {/* Side column skeleton */}
      <div className="lg:col-span-5 xl:col-span-4 space-y-6">
        {/* HUD card */}
        <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="h-4 w-16 animate-pulse rounded bg-gray-200" />
            <div className="h-4 w-10 animate-pulse rounded bg-gray-200" />
          </div>
          <div className="mt-3 h-2 w-full animate-pulse rounded-full bg-gray-100" />
          <div className="mt-2 grid grid-cols-3 gap-2">
            <div className="h-10 animate-pulse rounded-lg bg-gray-100" />
            <div className="h-10 animate-pulse rounded-lg bg-gray-100" />
            <div className="h-10 animate-pulse rounded-lg bg-gray-100" />
          </div>
        </div>

        {/* Stats panel */}
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 animate-pulse rounded-lg bg-gray-100" />
            <div className="h-4 w-24 animate-pulse rounded bg-gray-200" />
          </div>

          {/* Overall mini progress */}
          <div className="mt-4 space-y-2">
            <div className="h-3 w-1/3 animate-pulse rounded bg-gray-200" />
            <div className="h-2 w-full animate-pulse rounded-full bg-gray-100" />
          </div>

          {/* Category bars */}
          <div className="mt-5 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-3 w-1/2 animate-pulse rounded bg-gray-200" />
                <div className="h-2 w-full animate-pulse rounded-full bg-gray-100" />
              </div>
            ))}
          </div>

          {/* Quote */}
          <div className="mt-5 h-16 w-full animate-pulse rounded-xl bg-gray-100" />
        </div>
      </div>
    </div>
  );
}
