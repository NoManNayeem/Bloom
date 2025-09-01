# self_analysis/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    QuestionViewSet,
    OptionViewSet,
    TraitViewSet,
    AnswerViewSet,
    SelfAnalysisViewSet,
)

app_name = "self_analysis"

router = DefaultRouter()
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"options", OptionViewSet, basename="option")
router.register(r"traits", TraitViewSet, basename="trait")
router.register(r"answers", AnswerViewSet, basename="answer")
router.register(r"self-analysis", SelfAnalysisViewSet, basename="self-analysis")

urlpatterns = [
    path("", include(router.urls)),
]
