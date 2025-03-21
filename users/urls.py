
from django.urls import path

from . import views
from .views import MyLoginView, UserLogoutView, RegisterView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(http_method_names = ['get', 'post', 'options']), name='logout'),
    path('users_home/', views.users_home, name='users_home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='users_profile'),


]