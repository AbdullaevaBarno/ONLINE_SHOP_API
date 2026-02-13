from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'phone_number', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Jeke maǵlıwmatlar', {'fields': ('first_name', 'last_name', 'address',  'role')}),
        ('Huqıqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Waqıtlar', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Qosımsha maǵlıwmatlar', {
            'fields': ('role', 'phone_number', 'address')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")