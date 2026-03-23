from django.urls import path

from users.apps import UsersConfig
from users.views import CustomLoginView, CustomLogoutView

app_name = UsersConfig.name

urlpatterns = [
    path("login/", CustomLoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]
