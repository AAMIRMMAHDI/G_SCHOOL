from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class LoginForm(AuthenticationForm):
    """Login form."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input with-icon',
            'placeholder': _('Username'),
        }),
        label=_('Username')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input with-icon',
            'placeholder': _('Password'),
        }),
        label=_('Password')
    )

class RegisterForm(forms.ModelForm):
    """Registration form."""
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input with-icon',
            'placeholder': _('Password'),
        }),
        label=_('Password')
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input with-icon',
            'placeholder': _('Confirm Password'),
        }),
        label=_('Confirm Password')
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input with-icon', 'placeholder': _('Username')}),
            'email': forms.EmailInput(attrs={'class': 'form-input with-icon', 'placeholder': _('Email')}),
            'first_name': forms.TextInput(attrs={'class': 'form-input with-icon', 'placeholder': _('Full Name')}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input with-icon', 'placeholder': '09xxxxxxxxx'}),
        }
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'first_name': _('Full Name'),
            'phone_number': _('Phone Number'),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords do not match.'))
        return cleaned_data