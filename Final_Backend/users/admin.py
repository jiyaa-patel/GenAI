from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from .models import User

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'display_name', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'display_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('display_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'display_name'),
        }),
    )

# Custom LogEntry admin to handle UUID foreign keys
@admin.register(LogEntry)
class CustomLogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
    list_filter = ('action_time', 'action_flag', 'content_type')
    search_fields = ('user__email', 'object_repr', 'change_message')
    date_hierarchy = 'action_time'
    ordering = ('-action_time',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
