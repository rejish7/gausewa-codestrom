from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone_number', 'district', 'is_citizen', 'preferred_language', 'is_staff']
    list_filter = ['is_citizen', 'preferred_language', 'district', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone_number', 'district']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'district', 'is_citizen', 'preferred_language')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'district', 'is_citizen', 'preferred_language')
        }),
    )
