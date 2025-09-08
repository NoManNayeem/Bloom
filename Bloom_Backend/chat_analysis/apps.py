from django.apps import AppConfig


class ChatAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_analysis'
    
    def ready(self):
        # Import agents to ensure they're initialized
        try:
            from . import agents  # noqa
        except ImportError:
            pass
