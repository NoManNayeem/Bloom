# self_analysis/agents.py
"""
Agno Agents for Answer Validation & Analysis (TEXT-only AI)

- We ONLY invoke AI for TEXT questions.
- For MCQ/CHECKBOX:
    • validate_with_agent(...)  -> {"is_answer_ok": True}
    • analyze_with_agent(...)   -> {"positive": {}, "negative": {}, "quote": ""}

Setup
-----
pip install -U agno openai python-dotenv pydantic

.env (at project root; same directory as settings.BASE_DIR):
OPENAI_API_KEY=sk-...

Only OPENAI_API_KEY is read from .env. All other settings are hardcoded.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

# --------------------------- Load .env for OPENAI_API_KEY ---------------------------
try:
    from dotenv import load_dotenv
except Exception as _e:
    raise ImportError("python-dotenv is required. Install with `pip install python-dotenv`.") from _e


def _load_env_for_openai() -> None:
    """Load .env from settings.BASE_DIR or CWD without overriding existing env vars."""
    candidates = []
    try:
        from django.conf import settings  # type: ignore
        base_dir = getattr(settings, "BASE_DIR", None)
        if base_dir:
            candidates.append(Path(base_dir) / ".env")
    except Exception:
        pass
    candidates.append(Path.cwd() / ".env")
    loaded = False
    for dot in candidates:
        if dot.exists():
            load_dotenv(dotenv_path=dot, override=False)
            loaded = True
            break
    if not loaded:
        load_dotenv(override=False)


_load_env_for_openai()


def _ensure_openai_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your .env (settings.BASE_DIR/.env) "
            "or export it in the environment."
        )


# --------------------------- Agno / OpenAI ---------------------------
try:
    from agno.agent import Agent, RunResponse
    from agno.models.openai import OpenAIChat
except Exception as _e:
    raise ImportError("Agno is required. Install with `pip install agno openai`.") from _e


# --------------------------- Hardcoded settings ---------------------------
VALIDATE_MODEL = "gpt-4o-mini"
ANALYSIS_MODEL = "gpt-4o"
MIN_TEXT_WORDS = 5
MIN_TEXT_CHARS = 30


# --------------------------- Pydantic response models ---------------------------
class ValidationResult(BaseModel):
    is_answer_ok: bool = Field(..., description="True if the answer is acceptable")
    # NOTE: Key intentionally misspelled to match required wire format.
    instrcutions: Optional[str] = Field(
        None, description="Only when is_answer_ok=false. Short, actionable steps to fix."
    )


class PersonalityTraits(BaseModel):
    positive: Dict[str, int] = Field(..., description="Positive traits 0..100 (ints)")
    negative: Dict[str, int] = Field(..., description="Negative traits 0..100 (ints)")
    quote: str = Field(..., description="Motivational/insightful quote (<= 140 chars)")


# --------------------------- Agents (used only for TEXT) ---------------------------
_validate_agent = Agent(
    model=OpenAIChat(id=VALIDATE_MODEL),
    response_model=ValidationResult,
    structured_outputs=True,
    markdown=False,
    instructions=(
        "You are the Question Validate Agent for a self-analysis survey.\n"
        "Decide if the user's TEXT answer is acceptable for the given question.\n\n"
        "Requirements for acceptance:\n"
        f"- At least {MIN_TEXT_WORDS} words AND {MIN_TEXT_CHARS} characters.\n"
        "- Avoid placeholders (e.g., 'N/A', 'none', 'yes', 'no').\n"
        "- If the question asks 'when', include a time reference (e.g., month/year).\n"
        "- Do not use links; summarize in your own words.\n\n"
        "Output ONLY the fields in your response model. If unacceptable, include concise 'instrcutions'."
    ),
)

_analysis_agent = Agent(
    model=OpenAIChat(id=ANALYSIS_MODEL),
    response_model=PersonalityTraits,
    structured_outputs=True,
    markdown=False,
    instructions=(
        "You are the Answer Analysis Agent for a self-analysis survey.\n"
        "Analyze the user's TEXT answer and infer personality traits.\n\n"
        "Return two dicts: 'positive' and 'negative' (2–8 traits each when possible). "
        "Keys are short Title Case trait names (e.g., 'Confidence', 'Leadership', 'Anxiety'). "
        "Values are integers 0..100. Base your inference on the content; avoid fabrications.\n"
        "Also include a short motivational 'quote' (<= 140 chars).\n"
        "Output ONLY the fields specified in the response model."
    ),
)


# --------------------------- Public helpers ---------------------------
def validate_with_agent(question: Any, answer: Any, user: Any = None, timeout: Optional[int] = 30) -> Dict[str, Any]:
    """
    TEXT-only validation with AI. For MCQ/CHECKBOX we auto-approve.

    Returns:
      {"is_answer_ok": bool, "instrcutions": str?}
    """
    if not _is_text_question(question):
        return {"is_answer_ok": True}

    _ensure_openai_key()

    q_payload = _question_payload(question)
    a_payload = _format_answer_for_llm(answer)

    # Quick local pre-checks to save tokens:
    if not _passes_min_length(a_payload):
        return {
            "is_answer_ok": False,
            "instrcutions": f"Please expand your answer to at least {MIN_TEXT_WORDS} words and {MIN_TEXT_CHARS} characters, "
                            "adding specifics (when/where, your role, concrete outcome).",
        }
    if _looks_placeholder(a_payload):
        return {
            "is_answer_ok": False,
            "instrcutions": "Avoid placeholders like 'N/A' or one-word replies. Share specific details.",
        }
    if _question_demands_time(q_payload) and not _contains_time_reference(a_payload):
        return {
            "is_answer_ok": False,
            "instrcutions": "Mention when it happened (month/year, season, or timeframe).",
        }
    if "http://" in a_payload.lower() or "https://" in a_payload.lower():
        return {
            "is_answer_ok": False,
            "instrcutions": "Please summarize in your own words instead of linking.",
        }

    task = (
        "Decide if the following TEXT answer is acceptable for the question.\n\n"
        f"Question:\n{q_payload}\n\n"
        f"Answer:\n{a_payload}\n"
    )

    run: RunResponse = _validate_agent.run(task, timeout=timeout)
    content = run.content
    if isinstance(content, ValidationResult):
        return content.model_dump()
    if isinstance(content, dict):
        return {
            "is_answer_ok": bool(content.get("is_answer_ok", False)),
            **({"instrcutions": content.get("instrcutions")} if content.get("is_answer_ok") is False else {}),
        }
    # Defensive accept
    return {"is_answer_ok": True}


def analyze_with_agent(question: Any, answer: Any, user: Any = None, timeout: Optional[int] = 45) -> Dict[str, Any]:
    """
    TEXT-only analysis with AI. For MCQ/CHECKBOX we return empty analysis.

    Returns:
      {"positive": {...}, "negative": {...}, "quote": str}
    """
    if not _is_text_question(question):
        return {"positive": {}, "negative": {}, "quote": ""}

    _ensure_openai_key()

    q_payload = _question_payload(question)
    a_payload = _format_answer_for_llm(answer)

    task = (
        "Analyze the user's TEXT answer and infer personality traits and a short motivational quote.\n\n"
        f"Question:\n{q_payload}\n\n"
        f"Answer:\n{a_payload}\n"
    )

    run: RunResponse = _analysis_agent.run(task, timeout=timeout)
    content = run.content

    if isinstance(content, PersonalityTraits):
        data = content.model_dump()
    elif isinstance(content, dict):
        data = {
            "positive": dict(content.get("positive") or {}),
            "negative": dict(content.get("negative") or {}),
            "quote": str(content.get("quote") or "").strip(),
        }
    else:
        data = {"positive": {}, "negative": {}, "quote": ""}

    # Clamp/clean values and trim quote
    data["positive"] = {k: _clamp_0_100(v) for k, v in (data.get("positive") or {}).items()}
    data["negative"] = {k: _clamp_0_100(v) for k, v in (data.get("negative") or {}).items()}
    data["quote"] = (data.get("quote") or "")[:140].strip()

    return data


# --------------------------- Internals ---------------------------
def _is_text_question(q: Any) -> bool:
    """Detect if question is TEXT by tolerant string compare."""
    try:
        qtype = getattr(q, "type", None) or (q.get("type") if isinstance(q, dict) else None)
        return str(qtype).lower() == "text"
    except Exception:
        return False


def _question_payload(q: Any) -> str:
    if q is None:
        return "N/A"
    try:
        q_text = getattr(q, "text", None) or (q.get("text") if isinstance(q, dict) else "")
        q_type = getattr(q, "type", None) or (q.get("type") if isinstance(q, dict) else "")
        q_required = getattr(q, "required", None)
        if q_required is None and isinstance(q, dict):
            q_required = q.get("required")
        q_category = (
            getattr(q, "category", None)
            if hasattr(q, "category")
            else (q.get("category") if isinstance(q, dict) else None)
        )
        return f"[type={q_type}; required={bool(q_required)}; category={q_category}] {q_text}"
    except Exception:
        return str(q)


def _format_answer_for_llm(answer: Any) -> str:
    if isinstance(answer, str):
        return answer.strip()
    if isinstance(answer, dict):
        # For TEXT, we expect {"text": "..."} too—prefer that if present
        if "text" in answer and isinstance(answer["text"], str):
            return answer["text"].strip()
        # Fallback readable serialization
        return ", ".join(f"{k}={v}" for k, v in answer.items())
    if isinstance(answer, list):
        return ", ".join(str(v) for v in answer)
    return str(answer)


def _word_count(text: str) -> int:
    return len([w for w in text.strip().split() if w])


def _passes_min_length(text: str) -> bool:
    return len(text.strip()) >= MIN_TEXT_CHARS and _word_count(text) >= MIN_TEXT_WORDS


def _looks_placeholder(text: str) -> bool:
    t = text.strip().lower()
    return t in {"n/a", "na", "none", "nothing", "yes", "no"} or len(t) <= 2


def _question_demands_time(q_payload: str) -> bool:
    qp = q_payload.lower()
    return "when did it take place" in qp or qp.startswith("[type=text") and " when " in qp


def _contains_time_reference(text: str) -> bool:
    t = text.lower()
    # simple heuristics for month/year/day references
    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december",
        "jan","feb","mar","apr","jun","jul","aug","sep","sept","oct","nov","dec",
    ]
    if any(m in t for m in months):
        return True
    # year like 1990-2099
    import re
    if re.search(r"\b(19|20)\d{2}\b", t):
        return True
    # relative phrases
    rel = ["last year", "this year", "last month", "this month", "yesterday", "last week", "recently"]
    return any(p in t for p in rel)


def _clamp_0_100(val: Any) -> int:
    try:
        n = int(round(float(val)))
    except Exception:
        n = 0
    return max(0, min(100, n))
