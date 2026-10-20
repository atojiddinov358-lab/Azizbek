from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("archive/", views.archive_list, name="archive"),
    path("archive/surprise/", views.surprise, name="surprise"),
    path("archive/<slug:slug>/", views.article_detail, name="article"),
]
