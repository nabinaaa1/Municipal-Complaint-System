from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'ward', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'ward', 'created_at']
    search_fields = ['user__fullname', 'user__email', 'description']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Complaint Info', {
            'fields': ('user', 'ward', 'category', 'description', 'image')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )