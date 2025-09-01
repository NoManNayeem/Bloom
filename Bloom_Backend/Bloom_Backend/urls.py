from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# --- Admin branding ---
admin.site.site_header = "Bloom Admin"
admin.site.site_title = "Bloom Admin Portal"
admin.site.index_title = "Welcome to Bloom"

# --- Swagger / OpenAPI schema ---
schema_view = get_schema_view(
    openapi.Info(
        title="Bloom API",
        default_version="v1",
        description="API documentation for Bloom",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # App routes
    path("accounts/", include("accounts.urls")),            # e.g., register/login/me
    path("self-analysis/", include("self_analysis.urls")),

    # API Docs
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/schema.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]

# Static & media (for development)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=getattr(settings, "STATIC_ROOT", None))
    urlpatterns += static(getattr(settings, "MEDIA_URL", "/media/"), document_root=getattr(settings, "MEDIA_ROOT", None))
