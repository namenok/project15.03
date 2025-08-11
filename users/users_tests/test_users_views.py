import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_login_view(client):
    User.objects.create_user(username="testuser", password="pass1234")
    url = reverse("users:login")
    response = client.post(url, {"username": "testuser", "password": "pass1234"})
    assert response.status_code == 302
    assert response.url


@pytest.mark.django_db
def test_logout_view(client):
    User.objects.create_user(username="testuser2", password="pass1234")
    client.login(username="testuser2", password="pass1234")
    url = reverse("users:logout")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("users:login")


@pytest.mark.django_db
def test_register_view_get(client):
    url = reverse("users:register")
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_register_view_post_valid(client):
    url = reverse("users:register")
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(username="johndoe").exists()


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
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_profile_view_get(client):
    user = User.objects.create_user(username="profileuser", password="pass1234")
    user.profile.bio = "Initial bio"
    user.profile.save()
    client.login(username="profileuser", password="pass1234")
    url = reverse("users:users_profile")
    response = client.get(url)
    assert response.status_code == 200
    assert "user_form" in response.context
    assert "profile_form" in response.context


@pytest.mark.django_db
def test_profile_view_post_update_bio(client):
    user = User.objects.create_user(username="profileuser2", password="pass1234")
    user.profile.bio = "Initial bio"
    user.profile.save()
    client.login(username="profileuser2", password="pass1234")

    url = reverse("users:users_profile")
    data = {
        "action": "update_bio",
        "bio": "Updated bio",
    }
    response = client.post(url, data=data)
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.profile.bio == "Updated bio"


@pytest.mark.django_db
def test_profile_view_post_update_email(client):
    user = User.objects.create_user(
        username="profileuser3", password="pass1234", email="old@example.com"
    )
    user.profile.bio = "Initial bio"
    user.profile.save()
    client.login(username="profileuser3", password="pass1234")

    url = reverse("users:users_profile")
    data = {
        "action": "update_email",
        "username": "profileuser3",
        "email": "new@example.com",
    }
    response = client.post(url, data=data)
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.email == "new@example.com"


@pytest.mark.django_db
def test_profile_view_post_invalid(client):
    user = User.objects.create_user(username="profileuser4", password="pass1234")
    user.profile.bio = "Initial bio"
    user.profile.save()
    client.login(username="profileuser4", password="pass1234")

    url = reverse("users:users_profile")
    data = {
        "action": "update_email",
        "username": "",
        "email": "notanemail",
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert "user_form" in response.context
    assert "profile_form" in response.context
    assert response.context["user_form"].errors


@pytest.mark.django_db
def test_password_reset_view_get(client):
    url = reverse("users:password_reset")
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_password_change_view_get(client):
    User.objects.create_user(username="changepassuser", password="pass1234")
    client.login(username="changepassuser", password="pass1234")
    url = reverse("users:password_change")
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context
