from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Profile

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name','last_name' ,'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name','last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name','last_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio',)
    search_fields = ('user__email', 'bio')

admin.site.register(Profile, ProfileAdmin)