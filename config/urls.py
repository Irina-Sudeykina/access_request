from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('chaining/', include('smart_selects.urls')),
    path("", include("mis.urls", namespace="mis")),
    path("users/", include("users.urls", namespace="users")),
]
