'use client';

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

export default function AnswerInput({
  question,
  textAnswer,
  setTextAnswer,
  mcqOption,
  setMcqOption,
  checkboxOptions,
  setCheckboxOptions,
  highlightInvalid = false,
}) {
  if (!question) return null;

  if (question.type === 'text') {
    return (
      <AutoGrowTextarea
        rows={5}
        value={textAnswer}
        onChange={(e) => setTextAnswer(e.target.value)}
        placeholder="Include when/where, your role, what you did, and the outcome."
        aria-invalid={highlightInvalid ? 'true' : 'false'}
        className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none focus:ring-2 ${
          highlightInvalid
            ? 'border-amber-400 focus:border-amber-500 focus:ring-amber-200'
            : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-200'
        }`}
      />
    );
  }

  if (question.type === 'mcq') {
    return (
      <OptionsGrid>
        {question.options?.length ? (
          question.options.map((opt, idx) => {
            const selected = mcqOption === opt.id;
            return (
              <OptionCard
                key={opt.id}
                i={idx}
                selected={selected}
                onClick={() => setMcqOption(opt.id)}
              >
                <input
                  type="radio"
                  name={`q-${question.id}`}
                  className="peer sr-only"
                  checked={selected}
                  onChange={() => setMcqOption(opt.id)}
                />
                <span className="text-sm text-gray-800">{opt.label}</span>
              </OptionCard>
            );
          })
        ) : (
          <EmptyNote />
        )}
      </OptionsGrid>
    );
  }

  if (question.type === 'checkbox') {
    const toggle = (id) => {
      setCheckboxOptions((prev) =>
        prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
      );
    };

    return (
      <OptionsGrid>
        {question.options?.length ? (
          question.options.map((opt, idx) => {
            const selected = checkboxOptions.includes(opt.id);
            return (
              <OptionCard key={opt.id} i={idx} selected={selected} onClick={() => toggle(opt.id)}>
                <input
                  type="checkbox"
                  className="peer sr-only"
                  checked={selected}
                  onChange={() => toggle(opt.id)}
                />
                <span className="text-sm text-gray-800">{opt.label}</span>
              </OptionCard>
            );
          })
        ) : (
          <EmptyNote />
        )}
      </OptionsGrid>
    );
  }

  return <p className="text-sm text-gray-500">Unsupported question type.</p>;
}

/* ---------------- helpers ---------------- */

function OptionsGrid({ children }) {
  return (
    <motion.div
      className="grid grid-cols-1 gap-2 sm:grid-cols-2"
      initial="hidden"
      animate="show"
      variants={{
        hidden: { opacity: 1 },
        show: {
          opacity: 1,
          transition: { staggerChildren: 0.05, delayChildren: 0.02 },
        },
      }}
    >
      {children}
    </motion.div>
  );
}

function OptionCard({ children, selected, onClick, i }) {
  return (
    <motion.label
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
      onClick={onClick}
      variants={{
        hidden: { opacity: 0, y: 6 },
        show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 120, damping: 16, delay: 0.02 * i } },
      }}
      className={`group flex cursor-pointer items-center gap-3 rounded-xl border p-3 transition hover:bg-gray-50 focus:outline-none focus:ring-2 ${
        selected
          ? 'border-indigo-600 bg-indigo-50 ring-0'
          : 'border-gray-200 ring-indigo-200'
      }`}
    >
      {/* Visual marker */}
      <span
        className={`inline-block h-4 w-4 shrink-0 rounded-full border ${
          selected ? 'border-indigo-600 bg-indigo-600' : 'border-gray-300 bg-white'
        }`}
      />
      {children}
    </motion.label>
  );
}

function EmptyNote() {
  return <p className="text-xs text-gray-500">No options configured.</p>;
}

function AutoGrowTextarea({ value, onChange, ...props }) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = 'auto';
    // cap height to avoid infinite growth
    const max = 320; // px
    el.style.height = Math.min(el.scrollHeight, max) + 'px';
  }, [value]);

  return <textarea ref={ref} value={value} onChange={onChange} {...props} />;
}
