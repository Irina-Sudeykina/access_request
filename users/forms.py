from django.contrib.auth.forms import AuthenticationForm

from mis.forms import StyleFormMixin


class CustomLoginForm(StyleFormMixin, AuthenticationForm):
    pass
