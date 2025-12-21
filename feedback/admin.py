from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'complaint', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__fullname', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'