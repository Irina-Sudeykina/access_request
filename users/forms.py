from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm

from mis.forms import StyleFormMixin

from .models import User


class CustomLoginForm(StyleFormMixin, AuthenticationForm):
    pass
