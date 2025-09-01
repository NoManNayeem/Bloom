'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiGet, apiPost, getCookie } from '@/lib/api';

export function useSurvey() {
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [question, setQuestion] = useState(null);
  const [complete, setComplete] = useState(false);

  const [textAnswer, setTextAnswer] = useState('');
  const [mcqOption, setMcqOption] = useState(null);
  const [checkboxOptions, setCheckboxOptions] = useState([]);

  const [agentAdvice, setAgentAdvice] = useState('');

  const [progress, setProgress] = useState(null);
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    const token = getCookie('access_token');
    if (!token) {
      router.replace('/login?next=/home');
      return;
    }
    (async () => {
      try {
        setLoading(true);
        const [nextData, overviewData] = await Promise.all([
          apiGet('/self-analysis/answers/next/'),
          apiGet('/self-analysis/self-analysis/overview/'),
        ]);
        setQuestion(nextData.next_question);
        setComplete(nextData.complete);
        setProgress(nextData.progress);
        setOverview(overviewData);
        resetAnswerState(nextData.next_question);
      } catch (e) {
        setError(e.message || 'Failed to load');
      } finally {
        setLoading(false);
      }
    })();
  }, [router]);

  function resetAnswerState(nextQ) {
    setTextAnswer('');
    setMcqOption(null);
    setCheckboxOptions([]);
    setAgentAdvice('');
  }

  const buildAnswerPayload = () => {
    if (!question) return null;
    const base = { question: question.id };
    switch (question.type) {
      case 'text':
        return { ...base, answer: textAnswer?.trim() || '' };
      case 'mcq':
        return { ...base, answer: { option: mcqOption } };
      case 'checkbox':
        return { ...base, answer: { options: checkboxOptions } };
      default:
        return base;
    }
  };

  const canSubmit = useMemo(() => {
    if (!question) return false;
    if (question.type === 'text') return question.required ? !!textAnswer.trim() : true;
    if (question.type === 'mcq') return question.required ? !!mcqOption : true;
    if (question.type === 'checkbox') return question.required ? checkboxOptions.length > 0 : true;
    return true;
  }, [question, textAnswer, mcqOption, checkboxOptions]);

  const wordCount = useMemo(
    () => (textAnswer.trim() ? textAnswer.trim().split(/\s+/).length : 0),
    [textAnswer]
  );
  const charCount = useMemo(() => textAnswer.length, [textAnswer]);

  async function submit() {
    if (!question) return;
    setSubmitting(true);
    setError('');
    setAgentAdvice('');
    try {
      const payload = buildAnswerPayload();
      const data = await apiPost('/self-analysis/answers/answer-and-next/', payload);
      setQuestion(data.next_question);
      setComplete(data.complete);
      setProgress(data.progress);
      resetAnswerState(data.next_question);
      try {
        const ov = await apiGet('/self-analysis/self-analysis/overview/');
        setOverview(ov);
      } catch {}
    } catch (e) {
      if (e?.agent && e.agent.is_answer_ok === false) {
        setAgentAdvice(e.agent.instrcutions || 'Please refine your answer.');
      } else {
        setError(e.message || 'Submit failed');
      }
    } finally {
      setSubmitting(false);
    }
  }

  async function skip() {
    if (!question || question.required) return;
    setSubmitting(true);
    setError('');
    setAgentAdvice('');
    try {
      const payload = { question: question.id, answer: '' };
      const data = await apiPost('/self-analysis/answers/answer-and-next/', payload);
      setQuestion(data.next_question);
      setComplete(data.complete);
      setProgress(data.progress);
      resetAnswerState(data.next_question);
      try {
        const ov = await apiGet('/self-analysis/self-analysis/overview/');
        setOverview(ov);
      } catch {}
    } catch (e) {
      if (e?.agent && e.agent.is_answer_ok === false) {
        setAgentAdvice(e.agent.instrcutions || 'Please refine your answer.');
      } else {
        setError(e.message || 'Skip failed');
      }
    } finally {
      setSubmitting(false);
    }
  }

  async function recalc() {
    setSubmitting(true);
    setError('');
    try {
      await apiPost('/self-analysis/self-analysis/recalc/', {});
      const ov = await apiGet('/self-analysis/self-analysis/overview/');
      setOverview(ov);
    } catch (e) {
      setError(e.message || 'Recalc failed');
    } finally {
      setSubmitting(false);
    }
  }

  return {
    // state
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
    // derived
    canSubmit,
    wordCount,
    charCount,
    // actions
    submit,
    skip,
    recalc,
  };
}
