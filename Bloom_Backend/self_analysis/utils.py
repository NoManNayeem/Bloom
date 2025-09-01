# self_analysis/utils.py
from __future__ import annotations

from collections import Counter
from typing import Dict, Optional, Any, Iterable, Set

from .models import Question, Answer


# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------
def _answered_ids_for_user(user_id: int) -> Set[int]:
    """
    Returns a set of question IDs this user has already answered.
    """
    return set(
        Answer.objects.filter(user_id=user_id)
        .values_list("question_id", flat=True)
    )


def _all_active_questions() -> Iterable[Question]:
    """
    Returns all active questions in display order (root+subs).
    """
    return (
        Question.objects.filter(is_active=True)
        .select_related("parent")
        .order_by("order", "id")
    )


def _ancestors_answered(qid: int, parent_of: Dict[int, Optional[int]], answered_ids: Set[int]) -> bool:
    """
    Walk up the parent chain using the provided parent map and ensure all
    ancestors have been answered.
    """
    current = parent_of.get(qid)
    while current:
        if current not in answered_ids:
            return False
        current = parent_of.get(current)
    return True


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
def next_question_for_user(user) -> Optional[Question]:
    """
    Returns the first *eligible* active question the user hasn't answered yet.
    Eligibility rule:
      - If a question has a parent, all its ancestors must already be answered.
    Order: (order, id).
    """
    answered_ids = _answered_ids_for_user(user.id)

    # Build a parent lookup table (id -> parent_id) to avoid N queries
    qs = list(_all_active_questions())
    parent_of = {q.id: q.parent_id for q in qs}

    for q in qs:
        # Gate sub-questions until their parent chain is answered
        if q.parent_id and not _ancestors_answered(q.id, parent_of, answered_ids):
            continue
        if q.id not in answered_ids:
            return q
    return None


def progress_snapshot(user) -> Dict[str, Any]:
    """
    Returns an overall + category-wise progress snapshot.

    Structure:
    {
      "answered": 3,
      "total": 10,
      "percent": 30,
      "by_category": {
        "childhood": {"answered": 2, "total": 4, "percent": 50},
        "career":    {"answered": 1, "total": 3, "percent": 33},
        "":          {"answered": 0, "total": 3, "percent": 0}  # "" = no category
      }
    }
    """
    overall = _overall_progress(user)
    overall["by_category"] = _category_progress(user)
    return overall


def _overall_progress(user) -> Dict[str, int]:
    """
    Overall progress across all *active* questions (roots + sub-questions).
    """
    total = Question.objects.filter(is_active=True).count()
    answered = Answer.objects.filter(user=user, question__is_active=True).count()
    percent = int((answered / total) * 100) if total else 0
    return {"answered": answered, "total": total, "percent": percent}


def _category_progress(user) -> Dict[str, Dict[str, int]]:
    """
    Category-wise progress.
    Key is a string category; None is represented as empty string "" for JSON keys.
    """
    # Totals per category among active questions
    actives = Question.objects.filter(is_active=True).values_list("id", "category")
    totals = Counter((c or "") for (_id, c) in actives)

    # Answered counts per category for this user
    answered = Answer.objects.filter(
        user=user,
        question__is_active=True,
    ).values_list("question__category", flat=True)
    answered_counts = Counter((c or "") for c in answered)

    # Assemble
    by_cat: Dict[str, Dict[str, int]] = {}
    for cat, total in totals.items():
        a = answered_counts.get(cat, 0)
        by_cat[cat] = {
            "answered": a,
            "total": total,
            "percent": int((a / total) * 100) if total else 0,
        }
    return by_cat
