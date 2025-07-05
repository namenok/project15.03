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
    # Забув пароль (відправка листа)
    path("password-reset/", ResetPasswordView.as_view(), name="password_reset"),
    # Повідомлення "лист надіслано"
    path(
        "password-reset-sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_sent.html"
        ),
        name="password_reset_sent",
    ),
    # Ввід нового пароля з посилання в email
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Після підтвердження нового пароля
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Зміна пароля (авторизований користувач)
    path("password-change/", ChangePasswordView.as_view(), name="password_change"),
]
