from django.contrib import admin
from .models import Complaint, Remark

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


@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'complaint', 'admin_user', 'created_at_short', 'remark_preview']
    list_filter = ['created_at', 'admin_user']
    search_fields = ['remark', 'complaint__id', 'admin_user__fullname']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Remark Info', {
            'fields': ('complaint', 'admin_user', 'remark')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def created_at_short(self, obj):
        """Short date format for list display"""
        return obj.created_at.strftime("%b %d, %Y %I:%M %p")
    created_at_short.short_description = 'Created At'
    
    def remark_preview(self, obj):
        """Show first 50 characters of remark"""
        return obj.remark[:50] + '...' if len(obj.remark) > 50 else obj.remark
    remark_preview.short_description = 'Remark Preview'