# self_analysis/views.py
from __future__ import annotations

import logging
from typing import Optional

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Question, Option, Trait, Answer, SelfAnalysis
from .serializers import (
    QuestionSerializer,
    OptionSerializer,
    TraitSerializer,
    AnswerSerializer,
    SelfAnalysisSerializer,
    ProgressSerializer,
)
from .utils import next_question_for_user, progress_snapshot
from .permissions import IsAdminOrReadOnly
from .agents import validate_with_agent, analyze_with_agent

logger = logging.getLogger(__name__)


def _is_swagger_fake_view(view) -> bool:
    """
    drf-yasg sets `swagger_fake_view = True` during schema generation.
    Use this to avoid touching request.user (which is AnonymousUser then).
    """
    return getattr(view, "swagger_fake_view", False)


# ---------------------------------------------------------------------
# Questions (read for all; write only for staff)
# ---------------------------------------------------------------------
class QuestionViewSet(viewsets.ModelViewSet):
    """
    Query params:
      - parent=null   -> only root questions
      - parent=<id>   -> only children of <id>
      - category=<x>  -> filter by category
      - category=null -> only questions with no category
      - include_inactive=true (staff only) -> include inactive questions
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # Be defensive about user access in schema/anon contexts
        user = getattr(self.request, "user", None)
        is_staff = bool(user and getattr(user, "is_staff", False))

        include_inactive = self.request.query_params.get("include_inactive") == "true"
        qs = Question.objects.all().select_related("parent").prefetch_related("options", "children")
        if not include_inactive or not is_staff:
            qs = qs.filter(is_active=True)

        parent = self.request.query_params.get("parent")
        if parent == "null":
            qs = qs.filter(parent__isnull=True)
        elif parent:
            qs = qs.filter(parent_id=parent)

        category = self.request.query_params.get("category")
        if category == "null":
            qs = qs.filter(category__isnull=True)
        elif category:
            qs = qs.filter(category=category)

        return qs.order_by("order", "id")


# ---------------------------------------------------------------------
# Options (read for all; write only for staff)
# ---------------------------------------------------------------------
class OptionViewSet(viewsets.ModelViewSet):
    serializer_class = OptionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Option.objects.select_related("question")
        qid = self.request.query_params.get("question")
        if qid:
            qs = qs.filter(question_id=qid)
        return qs.order_by("question", "order", "id")


# ---------------------------------------------------------------------
# Traits catalog (read for all; write only for staff)
# ---------------------------------------------------------------------
class TraitViewSet(viewsets.ModelViewSet):
    serializer_class = TraitSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Trait.objects.all()
        pol = self.request.query_params.get("polarity")
        if pol in {"positive", "negative"}:
            qs = qs.filter(polarity=pol)
        is_active = self.request.query_params.get("is_active")
        if is_active in {"true", "false"}:
            qs = qs.filter(is_active=(is_active == "true"))
        return qs.order_by("name")


# ---------------------------------------------------------------------
# Answers (per-user)
# ---------------------------------------------------------------------
class AnswerViewSet(viewsets.ModelViewSet):
    """
    Extra actions:
      - GET  /self-analysis/answers/next/             -> next question + progress
      - POST /self-analysis/answers/answer-and-next/  -> upsert answer, recalc, return next + progress
      - GET  /self-analysis/answers/progress/         -> overall + by_category progress
    """
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Answer.objects.none()  # safe default for schema generation

    def get_queryset(self):
        # Short-circuit during schema gen or anon requests
        if _is_swagger_fake_view(self):
            return Answer.objects.none()
        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return Answer.objects.none()

        return (
            Answer.objects
            .select_related("question")
            .filter(user=user)
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="next")
    def next(self, request):
        q = next_question_for_user(request.user)
        prog = progress_snapshot(request.user)
        payload = {
            "next_question": QuestionSerializer(q, context={"request": request}).data if q else None,
            "complete": q is None,
            "progress": ProgressSerializer(prog).data,
        }
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="answer-and-next")
    def answer_and_next(self, request):
        """
        Flow:
          Text QnA -> Validator Agent -> if ok -> Analysis Agent -> store to DB
          Text QnA -> Validator Agent -> if NOT ok -> return 400 with instructions
          MCQ/Checkbox -> skip agents -> store to DB
        """
        data = request.data.copy()
        # defaults (kept for non-text answers; text will be overridden by agent analysis)
        data.setdefault("positive_values", {})
        data.setdefault("negative_values", {})
        data.setdefault("quote", "")

        ser = AnswerSerializer(data=data, context={"request": request})
        ser.is_valid(raise_exception=True)

        question: Question = ser.validated_data["question"]
        answer_payload = ser.validated_data.get("answer")

        # --- Agent gate for TEXT questions only ---
        try:
            is_text = str(getattr(question, "type", "")).lower() == "text"
        except Exception:
            is_text = False

        agent_feedback = None
        computed_positive = ser.validated_data.get("positive_values", {}) or {}
        computed_negative = ser.validated_data.get("negative_values", {}) or {}
        computed_quote = ser.validated_data.get("quote", "") or ""

        if is_text:
            try:
                # 1) Validate
                agent_feedback = validate_with_agent(question, answer_payload, user=request.user)
                if not agent_feedback.get("is_answer_ok", False):
                    # Do not save; return instructions for the FE to correct the answer
                    return Response(
                        {
                            "agent": agent_feedback,
                            "message": "Please improve your answer as suggested.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 2) Analyze (only after passing validation)
                try:
                    analysis = analyze_with_agent(question, answer_payload, user=request.user)
                except Exception as e:
                    logger.exception("Answer analysis agent failed; proceeding with empty traits. %s", e)
                    analysis = {"positive": {}, "negative": {}, "quote": ""}

                computed_positive = analysis.get("positive") or {}
                computed_negative = analysis.get("negative") or {}
                computed_quote = (analysis.get("quote") or "").strip()

            except Exception as e:
                # If validation agent fails unexpectedly, be forgiving: accept the answer and continue
                logger.exception("Validation agent error; accepting answer to avoid blocking. %s", e)

        # --- Persist Answer ---
        obj, _ = Answer.objects.update_or_create(
            user=request.user,
            question=question,
            defaults={
                "answer": answer_payload,
                "positive_values": computed_positive,
                "negative_values": computed_negative,
                "quote": computed_quote,
            },
        )

        # Keep SelfAnalysis up to date
        sa, _ = SelfAnalysis.objects.get_or_create(user=request.user)
        sa.recalc_from_answers()

        # Prepare next step payload
        q_next = next_question_for_user(request.user)
        prog = progress_snapshot(request.user)
        payload = {
            "saved_answer": AnswerSerializer(obj, context={"request": request}).data,
            "next_question": QuestionSerializer(q_next, context={"request": request}).data if q_next else None,
            "complete": q_next is None,
            "progress": ProgressSerializer(prog).data,
        }
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="progress")
    def progress(self, request):
        prog = progress_snapshot(request.user)
        return Response(ProgressSerializer(prog).data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------
# SelfAnalysis (per-user aggregated view)
# ---------------------------------------------------------------------
class SelfAnalysisViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Extra actions:
      - GET  /self-analysis/self-analysis/me/        -> current user's SelfAnalysis
      - POST /self-analysis/self-analysis/recalc/    -> recompute from Answers, returns payload
      - GET  /self-analysis/self-analysis/overview/  -> { self_analysis, progress }
    """
    serializer_class = SelfAnalysisSerializer
    permission_classes = [IsAuthenticated]
    queryset = SelfAnalysis.objects.none()  # satisfy schema generation

    def get_object(self) -> SelfAnalysis:
        # In normal requests, user is authenticated due to permission_classes
        obj, _ = SelfAnalysis.objects.get_or_create(user=self.request.user)
        return obj

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        obj = self.get_object()
        return Response(SelfAnalysisSerializer(obj).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="recalc")
    def recalc(self, request):
        obj = self.get_object()
        obj.recalc_from_answers()
        return Response(SelfAnalysisSerializer(obj).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="overview")
    def overview(self, request):
        sa = self.get_object()
        prog = progress_snapshot(request.user)
        data = {
            "self_analysis": SelfAnalysisSerializer(sa).data,
            "progress": ProgressSerializer(prog).data,
        }
        return Response(data, status=status.HTTP_200_OK)
