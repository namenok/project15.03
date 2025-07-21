from django.urls import path

from . import views
from .views import (
    MyLoginView,
    UserLogoutView,
    RegisterView,
    ProfileView,
    ResetPasswordView,
    ChangePasswordView,
    CustomPasswordResetConfirmView,
)

from django.contrib.auth import views as auth_views

app_name = "users"

urlpatterns = [
    path("account/login/", MyLoginView.as_view(), name="login"),
    path(
        "account/logout/",
        UserLogoutView.as_view(http_method_names=["get", "post", "options"]),
        name="logout",
    ),
    path("users_home/", views.users_home, name="users_home"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="users_profile"),
    # forgot passw-mail send
    path("password-reset/", ResetPasswordView.as_view(), name="password_reset"),
    # mail says "password reset link sent"
    path(
        "password-reset-sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_sent.html"
        ),
        name="password_reset_sent",
    ),
    # email enter new password after got resent link
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # after new pass confirmed
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # pass change for authorized user
    path("password-change/", ChangePasswordView.as_view(), name="password_change"),
]
