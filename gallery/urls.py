from django.urls import path

from . import views

app_name = "gallery"

urlpatterns = [
    path("", views.gallery, name="gallery"),
    path("uploads/", views.upload, name="upload"),
]
