from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery, name='gallery'), # це на перегляд галереї
    path('uploads/', views.upload, name='uploads')  # це на завантажити шось
]