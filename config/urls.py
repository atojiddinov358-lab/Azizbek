from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "The Hidden Archive"
handler404 = "core.views.not_found"
handler500 = "core.views.server_error"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("premium.urls")),
    path("", include("archive.urls")),
]
