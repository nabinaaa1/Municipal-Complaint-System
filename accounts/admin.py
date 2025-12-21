from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'fullname', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'fullname']
    
    # Add fullname, phone, address, ward to the form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('fullname', 'phone', 'address', 'ward')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('fullname', 'phone', 'address', 'ward')}),
    )