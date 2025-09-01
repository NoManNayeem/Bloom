# self_analysis/models.py
from django.conf import settings
from django.db import models
from collections import defaultdict


# ---------------------------------------------------------------------
# Base mixin for timestamps
# ---------------------------------------------------------------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------
# Questions & Options
# ---------------------------------------------------------------------
class Question(TimeStampedModel):
    """
    A survey item that can be:
      - Text (free text)
      - MCQ (single choice)
      - Checkbox (multiple choice)
    Supports optional nesting via `parent` for sub-questions, and a free-form
    `category` label used for grouping and progress breakdowns.
    """
    class QuestionType(models.TextChoices):
        TEXT = "text", "Text"
        MCQ = "mcq", "Multiple choice (single)"
        CHECKBOX = "checkbox", "Multiple choice (multiple)"

    text = models.TextField()
    type = models.CharField(max_length=16, choices=QuestionType.choices, default=QuestionType.TEXT)

    # Optional sub-questions via self-relation
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )

    # Free-form grouping; default None. Used by category-wise progress.
    category = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Q{self.pk}: {self.text[:80]}"


class Option(TimeStampedModel):
    """
    Choice options for MCQ/Checkbox questions.
    """
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)  # optional semantic value
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        unique_together = ("question", "label")
        ordering = ["order", "id"]

    def __str__(self):
        return f"Q{self.question_id} · {self.label}"


# ---------------------------------------------------------------------
# Traits catalog (dynamic)
# ---------------------------------------------------------------------
class Trait(TimeStampedModel):
    """
    Dynamic catalog of traits used across the system.
    Each trait belongs to a polarity bucket (positive/negative) so UIs and
    analytics can present/validate consistently. Trait values themselves
    (0–100) are stored per Answer/SelfAnalysis; this model defines the trait.
    """
    class Polarity(models.TextChoices):
        POSITIVE = "positive", "Positive"
        NEGATIVE = "negative", "Negative"

    # Display name / key (e.g., "Confidence", "Leadership", "Anxiety")
    name = models.CharField(max_length=64, unique=True)
    polarity = models.CharField(max_length=8, choices=Polarity.choices)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Optional bounds to guide UIs; values are stored elsewhere
    min_value = models.FloatField(default=0.0)
    max_value = models.FloatField(default=100.0)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["polarity", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.polarity})"


# ---------------------------------------------------------------------
# Answers (per-user, per-question) + dynamic trait scores
# ---------------------------------------------------------------------
class Answer(TimeStampedModel):
    """
    Stores one answer per user per question, plus dynamic maps of trait scores.

    `answer` payload schema:
      - TEXT      -> {"text": "free form text"}  (or serializer may normalize raw string)
      - MCQ       -> {"option": <option_id>}
      - CHECKBOX  -> {"options": [<option_id>, ...]}

    `positive_values` / `negative_values`:
      - {"Confidence": 85, "Leadership": 72, ...}  # 0–100 floats/ints
      - Keys are dynamic; optionally align with Trait.name.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)

    answer = models.JSONField(null=True, blank=True)

    positive_values = models.JSONField(default=dict, blank=True)
    negative_values = models.JSONField(default=dict, blank=True)

    quote = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "question")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "question"]),
            models.Index(fields=["question"]),
        ]

    def __str__(self):
        return f"Answer u={self.user_id} q={self.question_id}"


# ---------------------------------------------------------------------
# SelfAnalysis (aggregated per-user)
# ---------------------------------------------------------------------
class SelfAnalysis(TimeStampedModel):
    """
    Aggregated averages of a user's traits across all Answers.
    Keeps separate positive/negative maps, mirroring Answer structure.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="self_analysis", on_delete=models.CASCADE)
    combined_positives = models.JSONField(default=dict, blank=True)  # {"Confidence": 76.5, ...}
    combined_negatives = models.JSONField(default=dict, blank=True)  # {"Anxiety": 21.0, ...}
    quote = models.TextField(blank=True)  # policy: keep most recent non-empty from Answers

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"SelfAnalysis u={self.user_id}"

    # --------- Aggregation logic --------------------------------------
    def recalc_from_answers(self):
        """
        Recalculate combined_positives / combined_negatives as simple averages
        of all available Answer positive/negative maps for this user.
        """
        answers = self.user.answers.all()

        sums_pos, counts_pos = defaultdict(float), defaultdict(int)
        sums_neg, counts_neg = defaultdict(float), defaultdict(int)
        latest_quote = ""

        for a in answers:
            # positive traits
            for k, v in (a.positive_values or {}).items():
                try:
                    fv = float(v)
                except (TypeError, ValueError):
                    continue
                sums_pos[k] += fv
                counts_pos[k] += 1

            # negative traits
            for k, v in (a.negative_values or {}).items():
                try:
                    fv = float(v)
                except (TypeError, ValueError):
                    continue
                sums_neg[k] += fv
                counts_neg[k] += 1

            if a.quote:
                latest_quote = a.quote  # keep most recent non-empty

        self.combined_positives = {
            k: round(sums_pos[k] / counts_pos[k], 2) for k in sums_pos.keys() if counts_pos[k] > 0
        }
        self.combined_negatives = {
            k: round(sums_neg[k] / counts_neg[k], 2) for k in sums_neg.keys() if counts_neg[k] > 0
        }
        self.quote = latest_quote
        self.save(update_fields=["combined_positives", "combined_negatives", "quote", "updated_at"])
        return self
