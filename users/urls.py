
from django.urls import path

from . import views
from .views import MyLoginView, UserLogoutView, RegisterView, ResetPasswordView, ChangePasswordView
from django.contrib.auth.views import LogoutView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(http_method_names = ['get', 'post', 'options']), name='logout'),
    path('users_home/', views.users_home, name='users_home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='users_profile'),



    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_sent.html'),
         name='password_reset_sent'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

    path('password-change/', ChangePasswordView.as_view(), name='password_change'),


]