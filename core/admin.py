from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ExtendedUser

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'aprovado')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'aprovado')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Status', {'fields': ('aprovado',)}),
    )

admin.site.register(ExtendedUser, CustomUserAdmin)
