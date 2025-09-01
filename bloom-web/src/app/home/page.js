'use client';

import { useMemo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiRefreshCw, FiAlertCircle } from 'react-icons/fi';

import { useSurvey } from '@/hooks/useSurvey';
import StatsPanel from '@/components/survey/StatsPanel';
import QuestionForm from '@/components/survey/QuestionForm';
import { HomeSkeleton } from '@/components/survey/Skeletons';
import GamifiedHUD from '@/components/survey/GamifiedHUD';
import { blastConfetti } from '@/components/survey/ConfettiCelebration';

const fade = {
  hidden: { opacity: 0, y: 8 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.05 * i, type: 'spring', stiffness: 120, damping: 16 },
  }),
};

export default function HomePage() {
  const {
    loading,
    submitting,
    error,
    setError,
    question,
    complete,
    progress,
    overview,
    agentAdvice,
    setAgentAdvice,
    textAnswer,
    setTextAnswer,
    mcqOption,
    setMcqOption,
    checkboxOptions,
    setCheckboxOptions,
    canSubmit,
    wordCount,
    charCount,
    submit,
    skip,
    recalc,
  } = useSurvey();

  const answered = overview?.progress?.answered ?? 0;
  const percent = overview?.progress?.percent ?? 0;

  // lightweight XP heuristic: 20 per answer + 1 per 5% progress
  const xp = useMemo(() => answered * 20 + Math.round(percent / 5), [answered, percent]);

  // confetti on milestones & completion
  const prevPercent = useRef(percent);
  useEffect(() => {
    const milestones = [25, 50, 75, 100];
    const crossed = milestones.find((m) => prevPercent.current < m && percent >= m);
    if (crossed) blastConfetti({ scalar: crossed === 100 ? 1.2 : 1, spread: 80, particleCount: 120 });
    if (complete) blastConfetti({ scalar: 1.4, spread: 100, particleCount: 200 });
    prevPercent.current = percent;
  }, [percent, complete]);

  return (
    <main
      role="main"
      className="min-h-[calc(100svh-64px)] bg-gradient-to-br from-indigo-50 via-white to-pink-50"
    >
      <div className="relative mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="mb-6 flex flex-col gap-3 md:flex-row md:items-start md:justify-between"
          variants={fade}
          initial="hidden"
          animate="show"
        >
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Self Analysis</h1>
            <p className="mt-1 text-sm text-gray-600">
              Answer questions, earn XP, and watch your strengths emerge.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={recalc}
              disabled={submitting}
              className="rounded-xl border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm transition hover:-translate-y-0.5 hover:bg-gray-50 disabled:opacity-60"
              title="Recalculate self analysis"
            >
              <span className="inline-flex items-center gap-2">
                <FiRefreshCw className="h-4 w-4" />
                {submitting ? 'Recalculating…' : 'Recalculate'}
              </span>
            </button>
          </div>
        </motion.div>

        {/* Global error */}
        <AnimatePresence>
          {error && (
            <motion.div
              key="global-error"
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              className="mb-6 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
              role="alert"
              aria-live="polite"
            >
              <FiAlertCircle className="h-4 w-4" />
              <span className="flex-1">{error}</span>
              <button
                onClick={() => setError('')}
                className="ml-2 rounded px-2 py-1 text-xs text-red-700 underline hover:bg-red-100"
              >
                Dismiss
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Content */}
        {loading ? (
          <HomeSkeleton />
        ) : (
          <div className="grid gap-6 lg:grid-cols-12">
            {/* Main (wider) */}
            <motion.section
              variants={fade}
              custom={2}
              initial="hidden"
              animate="show"
              className="lg:col-span-7 xl:col-span-8"
            >
              {/* HUD (moved inside main column for tighter composition) */}
              <motion.div variants={fade} custom={1} initial="hidden" animate="show" className="mb-6">
                <GamifiedHUD answered={answered} percent={percent} xp={xp} />
              </motion.div>

              <QuestionForm
                question={question}
                complete={complete}
                progress={progress}
                agentAdvice={agentAdvice}
                textAnswer={textAnswer}
                setTextAnswer={(v) => {
                  setAgentAdvice(''); // clear agent tips as user edits
                  setTextAnswer(v);
                }}
                mcqOption={mcqOption}
                setMcqOption={setMcqOption}
                checkboxOptions={checkboxOptions}
                setCheckboxOptions={setCheckboxOptions}
                canSubmit={canSubmit}
                submitting={submitting}
                onSubmit={submit}
                onSkip={skip}
                wordCount={wordCount}
                charCount={charCount}
              />
            </motion.section>

            {/* Insights (sticky on large) */}
            <motion.aside
              variants={fade}
              custom={3}
              initial="hidden"
              animate="show"
              className="lg:col-span-5 xl:col-span-4"
            >
              <div className="lg:sticky lg:top-24">
                <StatsPanel overview={overview} />
              </div>
            </motion.aside>
          </div>
        )}
      </div>
    </main>
  );
}
