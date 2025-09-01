# self_analysis/management/commands/seed_self_analysis.py
# To run: python manage.py seed_self_analysis --reset

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction

from self_analysis.models import Question, Option, Trait


class Command(BaseCommand):
    help = "Seed a small set of Traits, Questions (with a couple sub-questions), and Options for quick local testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seeded data (Questions/Options/Traits) before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        reset = bool(opts.get("reset"))
        if reset:
            self.stdout.write(self.style.WARNING("Resetting existing data…"))
            Option.objects.all().delete()
            Question.objects.all().delete()
            Trait.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Cleared Options, Questions, Traits."))

        self._seed_traits()
        self._seed_questions_and_options()

        self.stdout.write(self.style.SUCCESS("✓ Seeding complete."))

    # ---------------------------------------------------------------------
    # Traits (minimal set for testing)
    # ---------------------------------------------------------------------
    def _seed_traits(self):
        self.stdout.write("Seeding traits…")

        positives = [
            ("Confidence", "Belief in one’s abilities"),
            ("Leadership", "Ability to guide and inspire others"),
            ("Empathy", "Understand and feel others’ emotions"),
            ("Creativity", "Generate novel and useful ideas"),
            ("Discipline", "Consistent effort & self-control"),
        ]
        negatives = [
            ("Anxiety", "Tendency to worry or feel nervous"),
            ("Procrastination", "Delaying important tasks"),
            ("Self-doubt", "Questioning one’s abilities"),
        ]

        created = 0
        for name, desc in positives:
            _, was_created = Trait.objects.get_or_create(
                name=name,
                defaults=dict(
                    polarity=Trait.Polarity.POSITIVE,
                    description=desc,
                    is_active=True,
                    min_value=0.0,
                    max_value=100.0,
                ),
            )
            created += int(was_created)

        for name, desc in negatives:
            _, was_created = Trait.objects.get_or_create(
                name=name,
                defaults=dict(
                    polarity=Trait.Polarity.NEGATIVE,
                    description=desc,
                    is_active=True,
                    min_value=0.0,
                    max_value=100.0,
                ),
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f"  Traits upserted. Newly created: {created}"))

    # ---------------------------------------------------------------------
    # Questions & Options (ONLY 6 questions total)
    # ---------------------------------------------------------------------
    def _seed_questions_and_options(self):
        self.stdout.write("Seeding questions & options…")

        # We keep it tiny: 6 total questions:
        #   1) TEXT (required) + 1 sub-question (optional)  -> counts as 2
        #   2) MCQ (required)                                -> 1
        #   3) CHECKBOX (optional)                           -> 1
        #   4) TEXT (required)                               -> 1
        #   5) TEXT (optional, uncategorized)                -> 1
        #
        # Total = 6
        questions: List[Dict] = [
            # 1. TEXT (required) + sub-question
            dict(
                ref="q_childhood_root",
                text="Tell us a childhood memory you are proud of.",
                type=Question.QuestionType.TEXT,
                category="childhood",
                required=True,
                order=1,
                parent_ref=None,
            ),
            dict(
                ref="q_childhood_when",
                text="When did it take place? (month/year or your age)",
                type=Question.QuestionType.TEXT,
                category="childhood",
                required=False,
                order=2,
                parent_ref="q_childhood_root",
            ),

            # 2. MCQ (required)
            dict(
                ref="q_career_feel",
                text="In your last project, how did you feel overall?",
                type=Question.QuestionType.MCQ,
                category="career",
                required=True,
                order=3,
                parent_ref=None,
            ),

            # 3. CHECKBOX (optional)
            dict(
                ref="q_career_strengths",
                text="Which strengths did you use in that project?",
                type=Question.QuestionType.CHECKBOX,
                category="career",
                required=False,
                order=4,
                parent_ref=None,
            ),

            # 4. TEXT (required)
            dict(
                ref="q_challenge",
                text="Describe a challenge you overcame recently. What changed because of you?",
                type=Question.QuestionType.TEXT,
                category="self-management",
                required=True,
                order=5,
                parent_ref=None,
            ),

            # 5. TEXT (optional, uncategorized)
            dict(
                ref="q_daily_reflection",
                text="Share a short reflection about today (what went well and why).",
                type=Question.QuestionType.TEXT,
                category=None,  # intentionally uncategorized
                required=False,
                order=6,
                parent_ref=None,
            ),
        ]

        # Minimal options for MCQ / CHECKBOX
        options: Dict[str, List[Tuple[str, str]]] = {
            "q_career_feel": [
                ("Very Positive", "very_positive"),
                ("Positive", "positive"),
                ("Neutral", "neutral"),
                ("Negative", "negative"),
                ("Very Negative", "very_negative"),
            ],
            "q_career_strengths": [
                ("Leadership", "leadership"),
                ("Communication", "communication"),
                ("Creativity", "creativity"),
                ("Empathy", "empathy"),
                ("Discipline", "discipline"),
            ],
        }

        # Create Questions (roots first to resolve parents)
        ref_to_question: Dict[str, Question] = {}

        for q in [q for q in questions if q["parent_ref"] is None]:
            obj = self._upsert_question(q, parent=None)
            ref_to_question[q["ref"]] = obj

        for q in [q for q in questions if q["parent_ref"] is not None]:
            parent = ref_to_question.get(q["parent_ref"])
            if not parent:
                raise RuntimeError(f"Parent with ref='{q['parent_ref']}' not found while seeding.")
            obj = self._upsert_question(q, parent=parent)
            ref_to_question[q["ref"]] = obj

        # Create options
        total_opts_created = 0
        for ref, pairs in options.items():
            question = ref_to_question.get(ref)
            if not question:
                self.stdout.write(self.style.WARNING(f"  ! Skipping options for '{ref}': question not found"))
                continue
            if question.type not in (Question.QuestionType.MCQ, Question.QuestionType.CHECKBOX):
                self.stdout.write(
                    self.style.WARNING(f"  ! Skipping options for '{ref}': question type is {question.type}")
                )
                continue

            for idx, (label, value) in enumerate(pairs, start=1):
                _, created = Option.objects.get_or_create(
                    question=question,
                    label=label,
                    defaults=dict(value=value, order=idx),
                )
                total_opts_created += int(created)

        self.stdout.write(self.style.SUCCESS(f"  Questions upserted: {len(ref_to_question)}"))
        self.stdout.write(self.style.SUCCESS(f"  Options created (new): {total_opts_created}"))

    def _upsert_question(self, qdata: Dict, parent: Optional[Question]) -> Question:
        """
        Create or update a Question by (text, type, parent, category).
        We use get_or_create to avoid duplicates on repeated seeding.
        """
        defaults = dict(
            required=qdata["required"],
            is_active=True,
            order=qdata["order"],
            category=qdata.get("category"),
        )
        obj, created = Question.objects.get_or_create(
            text=qdata["text"],
            type=qdata["type"],
            parent=parent,
            category=qdata.get("category"),
            defaults=defaults,
        )
        if not created:
            changed = False
            for field, val in defaults.items():
                if getattr(obj, field) != val:
                    setattr(obj, field, val)
                    changed = True
            if changed:
                obj.save(update_fields=list(defaults.keys()))
        return obj
