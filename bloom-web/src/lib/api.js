'use client';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// cookie helper for Authorization header
export function getCookie(name) {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

export async function apiGet(path) {
  const token = getCookie('access_token');
  const res = await fetch(`${API_URL}${path}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data?.detail || `GET ${path} failed`;
    throw new Error(msg);
  }
  return data;
}

export async function apiPost(path, body) {
  const token = getCookie('access_token');
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    // bubble up validator agent response for TEXT answers
    if (data?.agent && data.agent.is_answer_ok === false) {
      const err = new Error(
        data?.message || data?.detail || data?.agent?.instrcutions || `POST ${path} failed`
      );
      err.agent = data.agent;
      throw err;
    }
    const fieldErr = data?.answer && typeof data.answer === 'string' ? ` (${data.answer})` : '';
    throw new Error((data?.detail || `POST ${path} failed`) + fieldErr);
  }
  return data;
}
