
from django.urls import path

from . import views
from .views import MyLoginView, UserLogoutView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(http_method_names = ['get', 'post', 'options']), name='logout'),


]