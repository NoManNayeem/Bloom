from django.db import models
from django.conf import settings

class ChatConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_message = models.TextField()
    agent_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_complete_answer = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']

class PersonalityTraits(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # This line is crucial
    question = models.TextField()
    full_answer = models.TextField()
    positive = models.JSONField()
    negative = models.JSONField()
    quote = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Personality traits"
        ordering = ['-analyzed_at']