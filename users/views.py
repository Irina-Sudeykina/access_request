from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from users.forms import CustomLoginForm


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "users/login.html"
    success_url = reverse_lazy("mis:access_request_list")


class CustomLogoutView(LogoutView):
    next_page = "/"
