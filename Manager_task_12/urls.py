from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse

# Swagger схема
schema_view = get_schema_view(
    openapi.Info(
        title="Task Manager API",
        default_version="v1",
        description="Документация для проекта Менеджер задач",
        contact=openapi.Contact(email="support@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

def ping(request):
    return HttpResponse("pong")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tasks.urls")),
    path("api/auth/", include("accounts.urls")),  # ✅ регистрация/логин/логаут
    path("ping/", ping),

    # Swagger / Redoc
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# Swagger Authorize настройка (JWT)
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
schema_view.authentication_classes = [BasicAuthentication, SessionAuthentication]
schema_view.security_definitions = {
    "Bearer": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "JWT авторизация. Формат: **Bearer <твой токен>**"
    }
}
