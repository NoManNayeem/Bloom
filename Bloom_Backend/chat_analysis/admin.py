from django.contrib import admin
from .models import ChatConversation, PersonalityTraits

class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message', 'agent_message', 'timestamp', 'is_complete_answer')
    list_filter = ('is_complete_answer', 'timestamp')
    search_fields = ('user__username', 'user_message', 'agent_message')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'

class PersonalityTraitsAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'analyzed_at', 'positive_traits_count', 'negative_traits_count')
    list_filter = ('analyzed_at',)
    search_fields = ('user__username', 'question', 'quote')
    ordering = ('-analyzed_at',)

    # Method to count the number of positive traits
    def positive_traits_count(self, obj):
        return len(obj.positive)

    # Method to count the number of negative traits
    def negative_traits_count(self, obj):
        return len(obj.negative)

    # You can set a custom title for the method columns
    positive_traits_count.short_description = 'Positive Traits Count'
    negative_traits_count.short_description = 'Negative Traits Count'

admin.site.register(ChatConversation, ChatConversationAdmin)
admin.site.register(PersonalityTraits, PersonalityTraitsAdmin)
