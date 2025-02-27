from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("app.urls", namespace="public")),
    path("admin/", include("_admin.urls", namespace="admin")),
    path("personal-banking/", include("_user.urls", namespace="user")),
    path("auth/secure/", include("accounts.urls", namespace="auth")),
    path("__reload__/", include("django_browser_reload.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
