from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import CustomUser, UserSession

# Unregister the default Group admin if we don't need it
# admin.site.unregister(Group)

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'department')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'department', 'is_active', 'is_staff')

@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'department', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'department', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('username',)
    actions = ['reset_password_to_default']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Role & Department', {'fields': ('role', 'employee_id', 'department')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional', {'fields': ('signature', 'is_active_operator')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'department', 'password1', 'password2'),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Override to use different forms for add and change"""
        if obj is None:
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)
    
    def reset_password_to_default(self, request, queryset):
        """Reset selected users' passwords to default pattern"""
        count = 0
        reset_info = []
        
        for user in queryset:
            # Set default password based on role
            if user.role:
                default_password = f"{user.role.split('_')[0]}123"
            else:
                default_password = "user123"
            
            user.set_password(default_password)
            user.save()
            reset_info.append(f"{user.username}: {default_password}")
            count += 1
        
        password_list = "\n".join(reset_info)
        self.message_user(
            request,
            f"Successfully reset passwords for {count} users:\n{password_list}",
            messages.SUCCESS
        )
    
    reset_password_to_default.short_description = "Reset passwords to default (role123)"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/reset-password/',
                self.admin_site.admin_view(self.reset_single_password),
                name='accounts_customuser_reset_password',
            ),
        ]
        return custom_urls + urls
    
    def reset_single_password(self, request, user_id):
        """Reset a single user's password with custom value"""
        user = get_object_or_404(CustomUser, pk=user_id)
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password', '')
            if new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, f"Password for {user.username} reset to: {new_password}")
                return redirect('admin:accounts_customuser_changelist')
        
        # Set default password based on role
        if user.role:
            suggested_password = f"{user.role.split('_')[0]}123"
        else:
            suggested_password = "user123"
        
        context = {
            'user': user,
            'suggested_password': suggested_password,
            'title': f'Reset Password for {user.username}',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/accounts/reset_password.html', context)

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'ip_address')
    list_filter = ('login_time', 'logout_time')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('login_time',)
    ordering = ('-login_time',)
