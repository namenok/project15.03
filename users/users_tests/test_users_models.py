import pytest
from django.contrib.auth.models import User
from users.models import Profile
from PIL import Image

from pathlib import Path


@pytest.mark.django_db
def test_profile_creation():
    user = User.objects.create_user(username="testuser", password="pass1234")  # nosec
    profile = user.profile  # get the profile auto-created by the signal  # nosec

    assert profile.user == user  # nosec
    assert str(profile) == user.username  # nosec


@pytest.mark.django_db
def test_profile_save_resizes_image(tmp_path, settings):
    # Create user
    user = User.objects.create_user(username="imguser", password="pass1234")  # nosec

    # Get or create profile (in case signals or previous tests auto-create)
    profile, created = Profile.objects.get_or_create(
        user=user, defaults={"bio": "Test bio"}  # nosec
    )

    # Create test image file
    image_path = tmp_path / "test_image.jpg"  # nosec
    img = Image.new("RGB", (200, 200), color="red")  # nosec
    img.save(image_path)  # nosec

    # Save image in media directory
    media_root = Path(settings.MEDIA_ROOT)  # nosec
    dest_dir = media_root / "profile_images"  # nosec
    dest_dir.mkdir(exist_ok=True, parents=True)  # nosec
    dest_path = dest_dir / "test_image.jpg"  # nosec
    img.save(dest_path)  # nosec

    # Assign avatar path relative to MEDIA_ROOT
    profile.avatar.name = "profile_images/test_image.jpg"  # nosec

    # Save profile (should update existing profile, not insert)
    profile.save()  # nosec

    resized_img = Image.open(dest_path)  # nosec
    assert resized_img.height <= 100  # nosec
    assert resized_img.width <= 100  # nosec


@pytest.mark.django_db
def test_profile_save_handles_missing_file(tmp_path, settings):
    user = User.objects.create_user(
        username="missingfileuser", password="pass1234"  # nosec
    )  # nosec

    profile, created = Profile.objects.get_or_create(
        user=user, defaults={"bio": "Test bio"}  # nosec
    )

    profile.avatar.name = "profile_images/nonexistent.jpg"  # nosec
    profile.save()  # nosec має пройти без помилки

    assert Profile.objects.filter(user=user).exists()  # nosec
