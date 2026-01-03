from django.contrib import admin
from .models import ComplainsCategory, Complaint


@admin.register(ComplainsCategory)
class ComplainsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_np', 'name_en', 'icon_name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name_np', 'name_en']
    ordering = ['order', 'name_np']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['complaint_id_short', 'citizen', 'category', 'title', 'status', 'is_offline_submission', 'created_at']
    list_filter = ['status', 'is_offline_submission', 'category', 'created_at']
    search_fields = ['complaint_id', 'title', 'description', 'citizen__username', 'citizen_phone']
    readonly_fields = ['complaint_id', 'created_at', 'updated_at', 'synced_at', 'client_created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Complaint Info', {
            'fields': ('complaint_id', 'category', 'title', 'description')
        }),
        ('Citizen Details', {
            'fields': ('citizen', 'citizen_phone')
        }),
        ('Media', {
            'fields': ('image', 'voice_note')
        }),
        ('Location', {
            'fields': ('location_text', 'latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'synced_at', 'client_created_at', 'is_offline_submission')
        }),
    )
    
    def complaint_id_short(self, obj):
        return str(obj.complaint_id)[:8]
    complaint_id_short.short_description = 'ID'
    
    actions = ['mark_as_resolved', 'mark_as_in_progress']
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='RESOLVED')
        self.message_user(request, f'{updated} complaints marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected as Resolved'
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='IN_PROGRESS')
        self.message_user(request, f'{updated} complaints marked as in progress.')
    mark_as_in_progress.short_description = 'Mark selected as In Progress'
