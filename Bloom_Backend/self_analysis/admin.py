# self_analysis/admin.py
from django import forms
from django.contrib import admin, messages
from django.db.models import JSONField
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _

from .models import Question, Option, Trait, Answer, SelfAnalysis


# ---------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------
try:
    # Django ≥3.1 has a nice JSON editor in admin
    from django.contrib.admin.widgets import AdminJSONFieldWidget
except Exception:  # pragma: no cover
    AdminJSONFieldWidget = forms.Textarea


# ---------------------------------------------------------------------
# Inlines & Formsets
# ---------------------------------------------------------------------
class OptionInlineFormSet(BaseInlineFormSet):
    """
    Prevent adding options to TEXT questions (MCQ/Checkbox only).
    """
    def clean(self):
        super().clean()
        parent_q = getattr(self, "instance", None)
        if not parent_q or parent_q.pk is None:
            return
        if parent_q.type == Question.QuestionType.TEXT:
            # If any non-deleted inline has content, block
            for form in self.forms:
                if form.cleaned_data.get("DELETE"):
                    continue
                label = (form.cleaned_data.get("label") or "").strip()
                value = (form.cleaned_data.get("value") or "").strip()
                if label or value:
                    raise forms.ValidationError(
                        _("Options are not allowed for TEXT questions. "
                          "Change the type to MCQ/Checkbox or remove options.")
                    )


class OptionInline(admin.TabularInline):
    model = Option
    formset = OptionInlineFormSet
    extra = 0
    fields = ("label", "value", "order")
    ordering = ("order", "id")
    verbose_name = _("Choice")
    verbose_name_plural = _("Choices (for MCQ/Checkbox only)")


# ---------------------------------------------------------------------
# Question
# ---------------------------------------------------------------------
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "short_text", "type", "category", "parent",
        "required", "is_active", "order", "children_count",
        "created_at", "updated_at",
    )
    list_filter = (
        "type", "is_active", "required",
        ("parent", admin.RelatedOnlyFieldListFilter),
        "category",
    )
    search_fields = ("text", "category")
    ordering = ("order", "id")
    inlines = [OptionInline]

    fieldsets = (
        (None, {
            "fields": ("text", "type", "parent", "category", "order")
        }),
        (_("Behavior"), {
            "fields": ("required", "is_active")
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
        }),
    )
    readonly_fields = ("created_at", "updated_at")

    def short_text(self, obj):
        return (obj.text[:80] + "…") if len(obj.text) > 80 else obj.text
    short_text.short_description = _("Question")

    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = _("Sub-Q count")


# ---------------------------------------------------------------------
# Trait
# ---------------------------------------------------------------------
@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "polarity", "is_active", "min_value", "max_value", "created_at", "updated_at")
    list_filter = ("polarity", "is_active")
    search_fields = ("name", "description")
    ordering = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "polarity", "description", "is_active")}),
        (_("Guidance"), {"fields": ("min_value", "max_value")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")


# ---------------------------------------------------------------------
# Answer
# ---------------------------------------------------------------------
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "question_type", "created_at", "updated_at")
    list_filter = ("question__type", "question__category", "created_at")
    search_fields = ("user__username", "user__email", "question__text")
    list_select_related = ("user", "question")
    autocomplete_fields = ("user", "question")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    formfield_overrides = {
        JSONField: {"widget": AdminJSONFieldWidget},
    }

    fieldsets = (
        (None, {"fields": ("user", "question", "answer")}),
        (_("Trait Scores (0–100)"), {"fields": ("positive_values", "negative_values")}),
        (_("Motivational Quote"), {"fields": ("quote",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )

    def question_type(self, obj):
        return obj.question.type if obj.question_id else "-"
    question_type.short_description = _("Q type")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Keep user's SelfAnalysis in sync after admin edits
        sa, _ = SelfAnalysis.objects.get_or_create(user=obj.user)
        sa.recalc_from_answers()
        messages.success(request, _("SelfAnalysis recalculated for user %(u)s.") % {"u": obj.user})

    def delete_queryset(self, request, queryset):
        # Capture impacted users before delete
        user_ids = set(queryset.values_list("user_id", flat=True))
        super().delete_queryset(request, queryset)
        # Recalc for each impacted user
        for uid in user_ids:
            try:
                sa = SelfAnalysis.objects.get(user_id=uid)
            except SelfAnalysis.DoesNotExist:
                continue
            sa.recalc_from_answers()
        if user_ids:
            messages.success(request, _("SelfAnalysis recalculated for affected users."))


# ---------------------------------------------------------------------
# SelfAnalysis
# ---------------------------------------------------------------------
@admin.register(SelfAnalysis)
class SelfAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "pos_keys", "neg_keys", "updated_at")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user",)
    readonly_fields = ("updated_at",)
    ordering = ("-updated_at",)

    formfield_overrides = {
        JSONField: {"widget": AdminJSONFieldWidget},
    }

    actions = ["recalc_selected"]

    def pos_keys(self, obj):
        return len(obj.combined_positives or {})
    pos_keys.short_description = _("Pos traits")

    def neg_keys(self, obj):
        return len(obj.combined_negatives or {})
    neg_keys.short_description = _("Neg traits")

    def recalc_selected(self, request, queryset):
        count = 0
        for sa in queryset.select_related("user"):
            sa.recalc_from_answers()
            count += 1
        self.message_user(request, _(f"Recalculated {count} SelfAnalysis record(s)."), level=messages.SUCCESS)
    recalc_selected.short_description = _("Recalculate from Answers")


# ---------------------------------------------------------------------
# Option (standalone)
# ---------------------------------------------------------------------
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "question", "order", "created_at", "updated_at")
    list_filter = (("question", admin.RelatedOnlyFieldListFilter), "question__type", "question__category")
    search_fields = ("label", "question__text")
    ordering = ("question", "order", "id")
    autocomplete_fields = ("question",)
