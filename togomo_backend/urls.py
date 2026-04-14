from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "togomo-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.marketplace.urls")),
    path("health/", health_check),
]
