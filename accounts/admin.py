from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'phone_number', 'is_approved', 'is_staff', 'is_active')
    list_editable = ('is_approved',)  # Make is_approved editable in the list view
    list_filter = ('is_approved', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'phone_number')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'email', 'phone_number', 'is_approved')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'phone_number', 'password1', 'password2', 'is_approved'),
        }),
    )
    readonly_fields = ('last_login', 'date_joined')
    actions = ['approve_users', 'unapprove_users']

    def approve_users(self, request, queryset):
        """Approve selected users by setting is_approved to True."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(f'{updated} user(s) successfully approved.'))
    approve_users.short_description = _('Approve selected users')

    def unapprove_users(self, request, queryset):
        """Unapprove selected users by setting is_approved to False."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, _(f'{updated} user(s) successfully unapproved.'))
    unapprove_users.short_description = _('Unapprove selected users')