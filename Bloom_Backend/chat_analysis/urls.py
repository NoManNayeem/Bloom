from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_api, name='chat-api'),
    path('history/', views.conversation_history, name='conversation-history'),
    path('analysis/', views.analysis_results, name='analysis-results'),
]