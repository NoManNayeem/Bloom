'use client';

import { FiSend, FiSkipForward, FiAlertCircle } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import AnswerInput from './AnswerInput';
import FancyProgress from './FancyProgress';

export default function QuestionForm({
  question,
  complete,
  progress,
  agentAdvice,
  textAnswer,
  setTextAnswer,
  mcqOption,
  setMcqOption,
  checkboxOptions,
  setCheckboxOptions,
  canSubmit,
  submitting,
  onSubmit,
  onSkip,
  wordCount,
  charCount,
}) {
  const percent = Math.max(0, Math.min(100, Number(progress?.percent ?? 0)));

  return (
    <motion.div
      className="rounded-3xl border border-gray-200 bg-white/80 p-6 shadow-sm backdrop-blur"
      initial={{ y: 8, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 110, damping: 16 }}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-gray-900">Your Survey</h2>
        <div
          className="rounded-full bg-indigo-50 px-3 py-1 text-xs text-indigo-700"
          aria-live="polite"
        >
          {progress?.answered ?? 0}/{progress?.total ?? 0} • {Math.round(percent)}%
        </div>
      </div>

      <div className="mt-4">
        <FancyProgress percent={percent} height={8} />
      </div>

      <AnimatePresence mode="wait">
        {!complete && question ? (
          <motion.form
            key={question.id}
            onSubmit={(e) => {
              e.preventDefault();
              onSubmit();
            }}
            className="mt-6 space-y-5"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.25 }}
            aria-labelledby={`q-title-${question.id}`}
          >
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <motion.p
                    id={`q-title-${question.id}`}
                    className="text-[15px] font-medium text-gray-900"
                    initial={{ scale: 0.99 }}
                    animate={{ scale: 1 }}
                  >
                    {question.text}
                  </motion.p>
                  {question.category && (
                    <span className="mt-1 inline-block rounded-full bg-indigo-50 px-2 py-0.5 text-[11px] font-medium text-indigo-700">
                      {String(question.category).toUpperCase()}
                    </span>
                  )}
                </div>
                {question.required && (
                  <span className="shrink-0 rounded bg-red-50 px-2 py-0.5 text-xs font-semibold text-red-600">
                    Required
                  </span>
                )}
              </div>

              <AnimatePresence initial={false}>
                {agentAdvice && (
                  <motion.div
                    key="agent-advice"
                    className="mt-2 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900"
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    role="status"
                    aria-live="assertive"
                  >
                    <FiAlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                    <p>{agentAdvice}</p>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="mt-2">
                <AnswerInput
                  question={question}
                  textAnswer={textAnswer}
                  setTextAnswer={setTextAnswer}
                  mcqOption={mcqOption}
                  setMcqOption={setMcqOption}
                  checkboxOptions={checkboxOptions}
                  setCheckboxOptions={setCheckboxOptions}
                  highlightInvalid={Boolean(agentAdvice) && question.type === 'text'}
                />
                {question.type === 'text' && (
                  <p className="mt-2 text-xs text-gray-500">
                    {wordCount} words · {charCount} characters
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center justify-end gap-3">
              <motion.button
                type="button"
                onClick={onSkip}
                disabled={submitting || (question?.required ?? false)}
                whileTap={{ scale: 0.97 }}
                className="inline-flex items-center gap-2 rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                <FiSkipForward className="h-4 w-4" />
                Skip
              </motion.button>

              <motion.button
                type="submit"
                disabled={!canSubmit || submitting}
                whileTap={{ scale: 0.97 }}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-pink-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:opacity-95 disabled:opacity-60"
              >
                <FiSend className="h-4 w-4" />
                {submitting ? 'Submitting…' : 'Submit'}
              </motion.button>
            </div>
          </motion.form>
        ) : (
          <motion.div
            key="done"
            className="py-12 text-center"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <p className="text-lg font-semibold text-gray-900">You’re all caught up 🎉</p>
            <p className="mt-1 text-sm text-gray-600">No more questions for now.</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
