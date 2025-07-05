import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from gallery.models import GalleryDay, PhotoGallery
from datetime import date


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", password="password123"
    )  # nosec


@pytest.fixture
def valid_image_file():
    return SimpleUploadedFile(
        name="test_image.png",
        content=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\xda\xed\xc1\x01\x01\x00\x00\x00\xc2\xa0\xf7Om\x00\x00\x00\x00IEND\xaeB`\x82",
        content_type="image/png",
    )


@pytest.fixture
def gallery_day(db, user):
    return GalleryDay.objects.create(user=user, date=date.today())


@pytest.fixture
def gallery_day_factory(db, user):
    def make_gallery_day(**kwargs):
        defaults = {"user": user, "date": date.today()}
        defaults.update(kwargs)
        return GalleryDay.objects.create(**defaults)

    return make_gallery_day


@pytest.fixture
def photo_factory(db):
    def make_photo(**kwargs):
        if "image" not in kwargs:
            kwargs["image"] = SimpleUploadedFile(
                name="test_image.png",
                content=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\xda\xed\xc1\x01\x01\x00\x00\x00\xc2\xa0\xf7Om\x00\x00\x00\x00IEND\xaeB`\x82",
                content_type="image/png",
            )
        return PhotoGallery.objects.create(**kwargs)

    return make_photo
