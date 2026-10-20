from django.urls import path
from . import views
urlpatterns = [path("premium/", views.info, name="premium")]
