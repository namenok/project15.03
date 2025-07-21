import pytest
from django.contrib.auth.models import User
from users.models import Profile
from PIL import Image

from pathlib import Path


@pytest.mark.django_db
def test_profile_creation():
    user = User.objects.create_user(username="testuser", password="pass1234")
    profile = user.profile

    assert profile.user == user
    assert str(profile) == user.username


@pytest.mark.django_db
def test_profile_save_resizes_image(tmp_path, settings):
    user = User.objects.create_user(username="imguser", password="pass1234")

    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={"bio": "Test bio"},
    )

    image_path = tmp_path / "test_image.jpg"
    img = Image.new("RGB", (200, 200), color="red")
    img.save(image_path)

    media_root = Path(settings.MEDIA_ROOT)
    dest_dir = media_root / "profile_images"
    dest_dir.mkdir(exist_ok=True, parents=True)
    dest_path = dest_dir / "test_image.jpg"
    img.save(dest_path)

    profile.avatar.name = "profile_images/test_image.jpg"

    profile.save()

    resized_img = Image.open(dest_path)
    assert resized_img.height <= 100
    assert resized_img.width <= 100


@pytest.mark.django_db
def test_profile_save_handles_missing_file(tmp_path, settings):
    user = User.objects.create_user(
        username="missingfileuser",
        password="pass1234",
    )

    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={"bio": "Test bio"},
    )

    profile.avatar.name = "profile_images/nonexistent.jpg"
    profile.save()

    assert Profile.objects.filter(user=user).exists()
