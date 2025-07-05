import os

import pytest
from django.contrib.auth.models import User
from users.forms import RegisterForm, UpdateUserForm, UpdateProfileForm

from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_register_form_valid_data():
    form_data = {
        "first_name": "John",  # nosec
        "last_name": "Doe",  # nosec
        "username": "johndoe",  # nosec
        "email": "john@example.com",  # nosec
        "password1": "strongPassword123",  # nosec
        "password2": "strongPassword123",  # nosec
    }
    form = RegisterForm(data=form_data)  # nosec
    assert form.is_valid()  # nosec


@pytest.mark.django_db
def test_register_form_email_unique_validation():
    # Create user with email
    User.objects.create_user(
        username="existing", email="john@example.com", password="12345"  # nosec
    )  # nosec
    form_data = {
        "first_name": "John",  # nosec
        "last_name": "Doe",  # nosec
        "username": "johndoe2",  # nosec
        "email": "john@example.com",  # duplicate email, nosec
        "password1": "strongPassword123",  # nosec
        "password2": "strongPassword123",  # nosec
    }
    form = RegisterForm(data=form_data)  # nosec
    assert not form.is_valid()  # nosec
    assert "email" in form.errors  # nosec
    assert form.errors["email"][0] == "Цей email вже використовується."  # nosec


@pytest.mark.django_db
def test_update_user_form_valid_data():
    user = User.objects.create_user(
        username="johndoe", email="john@example.com", password="12345"  # nosec
    )  # nosec
    form_data = {
        "username": "johnny",  # nosec
        "email": "johnny@example.com",  # nosec
    }
    form = UpdateUserForm(data=form_data, instance=user)  # nosec
    assert form.is_valid()  # nosec


@pytest.mark.django_db
def test_update_user_form_email_unique_validation():
    user1 = User.objects.create_user(
        username="user1", email="user1@example.com", password="12345"  # nosec
    )  # nosec
    user2 = User.objects.create_user(
        username="user2", email="user2@example.com", password="12345"  # nosec
    )  # nosec

    form_data = {
        "username": "user2",  # nosec
        "email": user1.email,  # use the variable explicitly, nosec
    }
    form = UpdateUserForm(data=form_data, instance=user2)  # nosec
    assert not form.is_valid()  # nosec
    assert "email" in form.errors  # nosec
    assert (
        form.errors["email"][0] == "Цей email вже використовується іншим користувачем."
    )  # nosec


@pytest.mark.django_db
def test_update_profile_form_valid_data():
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="12345"  # nosec
    )  # nosec

    # Get profile created by signal instead of creating manually
    profile = user.profile  # nosec

    image_content = (
        b"\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\x00\x00\x00\x00\x00"
        b"\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
        b"\x02\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
    )  # nosec
    uploaded_file = SimpleUploadedFile(
        "avatar.gif", image_content, content_type="image/gif"  # nosec
    )  # nosec

    form_data = {
        "bio": "Updated bio",  # nosec
    }
    form_files = {
        "avatar": uploaded_file,  # nosec
    }
    form = UpdateProfileForm(
        data=form_data, files=form_files, instance=profile  # nosec
    )  # nosec
    assert form.is_valid()  # nosec
    saved_profile = form.save()
    assert saved_profile.bio == "Updated bio"  # nosec

    # Robust filename check
    filename = os.path.basename(saved_profile.avatar.name)  # nosec
    assert filename.startswith("avatar")  # nosec
    assert filename.endswith(".gif")  # nosec
