import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_login_view(client):
    user = User.objects.create_user(username="testuser", password="pass1234")  # nosec
    assert user.username == "testuser"  # nosec
    url = reverse("users:login")
    response = client.post(
        url,
        {"username": "testuser", "password": "pass1234"},  # nosec
    )
    assert response.status_code == 302  # nosec
    assert response.url  # nosec


@pytest.mark.django_db
def test_logout_view(client):
    user = User.objects.create_user(username="testuser2", password="pass1234")  # nosec
    assert user.username == "testuser2"  # nosec
    client.login(username="testuser2", password="pass1234")  # nosec
    url = reverse("users:logout")
    response = client.get(url)
    assert response.status_code == 302  # nosec
    assert response.url == reverse("users:login")  # nosec


@pytest.mark.django_db
def test_register_view_get(client):
    url = reverse("users:register")
    response = client.get(url)
    assert response.status_code == 200  # nosec
    assert "form" in response.context  # nosec


@pytest.mark.django_db
def test_register_view_post_valid(client):
    url = reverse("users:register")
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "password1": "StrongPass123!",  # nosec
        "password2": "StrongPass123!",  # nosec
    }
    response = client.post(url, data)
    assert response.status_code == 302  # nosec
    assert User.objects.filter(username="johndoe").exists()  # nosec


@pytest.mark.django_db
def test_register_view_post_invalid(client):
    url = reverse("users:register")
    data = {
        "first_name": "",
        "last_name": "",
        "username": "",
        "email": "invalidemail",
        "password1": "123",
        "password2": "321",
    }
    response = client.post(url, data)
    assert response.status_code == 200  # nosec
    assert "form" in response.context  # nosec
    assert response.context["form"].errors  # nosec


@pytest.mark.django_db
def test_profile_view_get(client):
    user = User.objects.create_user(username="profileuser", password="pass1234")  # nosec
    assert user.username == "profileuser"  # nosec
    client.login(username="profileuser", password="pass1234")  # nosec
    url = reverse("users:users_profile")
    response = client.get(url)
    assert response.status_code == 200  # nosec
    assert "user_form" in response.context  # nosec
    assert "profile_form" in response.context  # nosec


@pytest.mark.django_db
def test_profile_view_post_valid(client, tmp_path, settings):
    user = User.objects.create_user(username="profileuser2", password="pass1234")  # nosec
    client.login(username="profileuser2", password="pass1234")  # nosec

    avatar_path = tmp_path / "avatar.png"
    avatar_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    )  # minimal PNG header  # nosec

    url = reverse("users:users_profile")
    data = {
        "username": "profileuser2",
        "email": "profileuser2@example.com",
        "bio": "Updated bio",
    }
    files = {
        "avatar": SimpleUploadedFile(
            str(avatar_path), avatar_path.read_bytes(), content_type="image/png"
        )  # nosec
    }
    response = client.post(url, data=data, files=files)
    assert response.status_code == 302  # nosec
    user.refresh_from_db()  # nosec
    assert user.profile.bio == "Updated bio"  # nosec


@pytest.mark.django_db
def test_profile_view_post_invalid(client):
    user = User.objects.create_user(username="profileuser3", password="pass1234")  # nosec
    assert user.username == "profileuser3"  # nosec

    client.login(username="profileuser3", password="pass1234")  # nosec

    url = reverse("users:users_profile")
    data = {
        "username": "",  # nosec
        "email": "notanemail",
        "bio": "",
    }
    response = client.post(url, data=data)
    assert response.status_code == 200  # nosec
    assert "user_form" in response.context  # nosec
    assert "profile_form" in response.context  # nosec
    assert response.context["user_form"].errors  # nosec
    assert response.context["profile_form"].errors  # nosec


@pytest.mark.django_db
def test_password_reset_view_get(client):
    url = reverse("users:password_reset")
    response = client.get(url)
    assert response.status_code == 200  # nosec
    assert "form" in response.context  # nosec


@pytest.mark.django_db
def test_password_change_view_get(client):
    user = User.objects.create_user(username="changepassuser", password="pass1234")  # nosec
    assert user.username == "changepassuser"  # nosec
    client.login(username="changepassuser", password="pass1234")  # nosec
    url = reverse("users:password_change")
    response = client.get(url)
    assert response.status_code == 200  # nosec
    assert "form" in response.context  # nosec
