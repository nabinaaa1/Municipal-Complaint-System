from django.contrib import admin
from .models import Complaint, Remark

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'ward', 'category', 'priority_badge', 'status', 'days_old', 'created_at']
    list_filter = ['status', 'priority', 'category', 'ward', 'created_at']
    search_fields = ['user__fullname', 'user__email', 'description']
    list_editable = ['status'] 
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'days_old_display']
    actions = ['mark_as_urgent', 'mark_as_normal', 'auto_update_priorities']
    
    fieldsets = (
        ('Complaint Info', {
            'fields': ('user', 'ward', 'category', 'description', 'image')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'days_old_display'),
            'classes': ('collapse',)
        }),
    )
    
    def priority_badge(self, obj):
        """Display priority with color badge"""
        if obj.priority == 'Urgent':
            return '🔴 Urgent'
        else:
            return '🟢 Normal'
    priority_badge.short_description = 'Priority'
    
    def days_old(self, obj):
        """Display days since creation with color coding"""
        days = obj.days_since_creation()
        if days >= 7:
            return f'🔴 {days} days'
        elif days >= 5:
            return f'🟡 {days} days'
        else:
            return f'🟢 {days} days'
    days_old.short_description = 'Age'
    
    def days_old_display(self, obj):
        """Display detailed age information"""
        return f"{obj.days_since_creation()} days old"
    days_old_display.short_description = 'Days Since Creation'
    
    def mark_as_urgent(self, request, queryset):
        """Admin action to mark complaints as urgent"""
        updated = queryset.update(priority='Urgent')
        self.message_user(request, f'{updated} complaint(s) marked as Urgent.')
    mark_as_urgent.short_description = 'Mark selected as Urgent'
    
    def mark_as_normal(self, request, queryset):
        """Admin action to mark complaints as normal"""
        updated = queryset.update(priority='Normal')
        self.message_user(request, f'{updated} complaint(s) marked as Normal.')
    mark_as_normal.short_description = 'Mark selected as Normal'
    
    def auto_update_priorities(self, request, queryset):
        """Admin action to auto-update priorities for old complaints"""
        updated = 0
        for complaint in queryset:
            if complaint.update_priority():
                updated += 1
        self.message_user(request, f'{updated} complaint(s) auto-updated to Urgent priority.')
    auto_update_priorities.short_description = 'Auto-update priorities (7+ days old)'


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