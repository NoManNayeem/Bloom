# self_analysis/serializers.py
from __future__ import annotations

from typing import Dict, Any, Optional

from django.db.models import QuerySet
from rest_framework import serializers

from .models import Question, Option, Trait, Answer, SelfAnalysis


# ---------------------------------------------------------------------
# Option
# ---------------------------------------------------------------------
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "label", "value", "order", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


# ---------------------------------------------------------------------
# Question (with nested children + options)
# ---------------------------------------------------------------------
class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "type",
            "parent",
            "category",
            "required",
            "is_active",
            "order",
            "options",
            "children",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_children(self, obj: Question):
        qs: QuerySet[Question] = obj.children.order_by("order", "id").prefetch_related("options", "children")
        return QuestionSerializer(qs, many=True, context=self.context).data


# ---------------------------------------------------------------------
# Trait (catalog)
# ---------------------------------------------------------------------
class TraitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trait
        fields = [
            "id",
            "name",
            "polarity",
            "description",
            "is_active",
            "min_value",
            "max_value",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ---------------------------------------------------------------------
# Flexible Dict field for trait scores (0–100)
# - Optionally validates against Trait table (polarity + bounds) if present
# ---------------------------------------------------------------------
class TraitScoresField(serializers.DictField):
    """
    Dict[str, number] where each value must be between 0 and 100 by default.
    If a given key matches a Trait.name, we also:
      - ensure the Trait is active
      - ensure polarity matches `expected_polarity` if provided
      - clamp/validate to trait min/max bounds (inclusive)
    """

    def __init__(self, *args, expected_polarity: Optional[str] = None, **kwargs):
        # Base numeric validation (0..100)
        kwargs.setdefault("child", serializers.FloatField(min_value=0.0, max_value=100.0))
        super().__init__(*args, **kwargs)
        self.expected_polarity = expected_polarity

    def to_internal_value(self, data: Any) -> Dict[str, float]:
        if not isinstance(data, dict):
            raise serializers.ValidationError("Must be an object with key: number pairs.")
        cleaned: Dict[str, float] = {}

        # Fetch all referenced traits in a single query
        names = [str(k) for k in data.keys()]
        traits = {t.name: t for t in Trait.objects.filter(name__in=names)} if names else {}

        errors: Dict[str, str] = {}
        for raw_key, raw_val in data.items():
            key = str(raw_key)
            try:
                val = float(raw_val)
            except (TypeError, ValueError):
                errors[key] = "Score must be a number."
                continue

            # Basic 0..100 constraint already on child field, but we recheck for clarity
            if val < 0 or val > 100:
                errors[key] = "Score must be between 0 and 100."
                continue

            tr = traits.get(key)
            if tr:
                if not tr.is_active:
                    errors[key] = "This trait is inactive."
                    continue
                if self.expected_polarity and tr.polarity != self.expected_polarity:
                    errors[key] = f"Expected a {self.expected_polarity} trait."
                    continue
                # Optional tighter bounds from catalog
                if val < tr.min_value or val > tr.max_value:
                    errors[key] = f"Must be between {tr.min_value:g} and {tr.max_value:g}."
                    continue

            cleaned[key] = val

        if errors:
            raise serializers.ValidationError(errors)
        return cleaned


# ---------------------------------------------------------------------
# Answer
# ---------------------------------------------------------------------
class AnswerSerializer(serializers.ModelSerializer):
    """
    Validates `answer` shape by Question.type:
      - text:     {"text": "..."}  (also accepts raw string and normalizes)
      - mcq:      {"option": <option_id>}
      - checkbox: {"options": [<option_id>, ...]}
    Trait values are Dict[str, 0..100].
    """
    positive_values = TraitScoresField(required=False, default=dict, expected_polarity="positive")
    negative_values = TraitScoresField(required=False, default=dict, expected_polarity="negative")

    class Meta:
        model = Answer
        fields = [
            "id",
            "user",
            "question",
            "answer",
            "positive_values",
            "negative_values",
            "quote",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    # ---- Core validation for the "answer" payload per question type ----
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        question: Optional[Question] = attrs.get("question") or getattr(self.instance, "question", None)
        payload = attrs.get("answer", None)

        # Nothing to validate if question missing (shouldn't happen in create)
        if question is None:
            return attrs

        qtype = question.type

        # Enforce required flag
        if question.required and (payload is None or payload == "" or payload == {}):
            raise serializers.ValidationError({"answer": "This question is required."})

        # If client omits answer on non-required, accept as is
        if payload is None:
            return attrs

        # TEXT normalizations/validation
        if qtype == Question.QuestionType.TEXT:
            if isinstance(payload, str):
                attrs["answer"] = {"text": payload}
            elif not (isinstance(payload, dict) and isinstance(payload.get("text"), str)):
                raise serializers.ValidationError(
                    {"answer": "For TEXT, use {'text': 'your answer'} or a raw string."}
                )

        # MCQ: ensure option belongs to this question
        elif qtype == Question.QuestionType.MCQ:
            option_id: Optional[int] = None
            if isinstance(payload, dict) and "option" in payload:
                option_id = payload["option"]
            elif isinstance(payload, int):
                option_id = payload
                attrs["answer"] = {"option": option_id}
            else:
                raise serializers.ValidationError({"answer": "For MCQ, use {'option': <option_id>}."})

            if not question.options.filter(id=option_id).exists():
                raise serializers.ValidationError({"answer": f"Option {option_id} is not valid for this question."})

        # CHECKBOX: ensure all options belong to this question
        elif qtype == Question.QuestionType.CHECKBOX:
            option_ids: Optional[list[int]] = None
            if isinstance(payload, dict) and "options" in payload and isinstance(payload["options"], list):
                option_ids = payload["options"]
            elif isinstance(payload, list):
                option_ids = payload
                attrs["answer"] = {"options": option_ids}
            else:
                raise serializers.ValidationError(
                    {"answer": "For CHECKBOX, use {'options': [<option_id>, ...]}."}
                )

            valid_ids = set(question.options.values_list("id", flat=True))
            if not option_ids or not set(option_ids).issubset(valid_ids):
                raise serializers.ValidationError({"answer": "One or more option ids are invalid for this question."})

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Answer:
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


# ---------------------------------------------------------------------
# SelfAnalysis
# ---------------------------------------------------------------------
class SelfAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfAnalysis
        fields = [
            "id",
            "user",
            "combined_positives",
            "combined_negatives",
            "quote",
            "updated_at",
            "created_at",
        ]
        read_only_fields = ["id", "user", "updated_at", "created_at"]


# ---------------------------------------------------------------------
# Progress snapshot (overall + by_category)
# ---------------------------------------------------------------------
class ProgressSerializer(serializers.Serializer):
    answered = serializers.IntegerField()
    total = serializers.IntegerField()
    percent = serializers.IntegerField()
    # by_category is a mapping[str, {"answered": int, "total": int, "percent": int}]
    by_category = serializers.JSONField()
