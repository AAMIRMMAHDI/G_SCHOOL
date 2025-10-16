from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import LoginForm, RegisterForm

def login_view(request):
    """Display and handle login form, restricted to admins or approved users."""
    if request.user.is_authenticated:
        return redirect('blog:send_list')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_approved:
                login(request, user)
                messages.success(request, _('✅ Successfully logged in!'))
                return redirect('blog:send_list')
            else:
                messages.error(request, _('❌ Your account is not approved yet.'))
        else:
            messages.error(request, _('❌ Invalid username or password.'))
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'login_form': form,
        'register_form': RegisterForm()
    })

def register_view(request):
    """Display and handle registration form, users need admin approval."""
    if request.user.is_authenticated:
        return redirect('blog:send_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_approved = False  # New users are not approved by default
            user.save()
            messages.success(request, _('🎉 Registration successful! Awaiting admin approval.'))
            return redirect('accounts:login')
        else:
            messages.error(request, _('⚠️ Please fix the form errors.'))
    else:
        form = RegisterForm()

    return render(request, 'accounts/login.html', {
        'register_form': form,
        'login_form': LoginForm()
    })