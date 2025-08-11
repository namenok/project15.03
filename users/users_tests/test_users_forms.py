import pytest
from django.contrib.auth.models import User
from users.forms import RegisterForm, UpdateUserForm, UpdateProfileForm


@pytest.mark.django_db
def test_register_form_valid_data():
    form_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "password1": "strongPassword123",
        "password2": "strongPassword123",
    }
    form = RegisterForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_register_form_email_unique_validation():
    User.objects.create_user(
        username="existing",
        email="john@example.com",
        password="12345",
    )
    form_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe2",
        "email": "john@example.com",
        "password1": "strongPassword123",
        "password2": "strongPassword123",
    }
    form = RegisterForm(data=form_data)
    assert not form.is_valid()
    assert "email" in form.errors
    assert form.errors["email"][0] == "Цей email вже використовується."


@pytest.mark.django_db
def test_update_user_form_valid_data():
    user = User.objects.create_user(
        username="johndoe",
        email="john@example.com",
        password="12345",
    )
    form_data = {
        "username": "johnny",
        "email": "johnny@example.com",
    }
    form = UpdateUserForm(data=form_data, instance=user)
    assert form.is_valid()


@pytest.mark.django_db
def test_update_user_form_email_unique_validation():
    user1 = User.objects.create_user(
        username="user1",
        email="user1@example.com",
        password="12345",
    )
    user2 = User.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="12345",
    )

    form_data = {
        "username": "user2",
        "email": user1.email,
    }
    form = UpdateUserForm(data=form_data, instance=user2)
    assert not form.is_valid()
    assert "email" in form.errors
    assert (
        form.errors["email"][0] == "Цей email вже використовується іншим користувачем."
    )


@pytest.mark.django_db
def test_update_profile_form_valid_data():
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="12345",
    )
    profile = user.profile

    form_data = {
        "bio": "Updated bio",
    }
    form = UpdateProfileForm(data=form_data, instance=profile)
    assert form.is_valid()

    saved_profile = form.save()
    assert saved_profile.bio == "Updated bio"
