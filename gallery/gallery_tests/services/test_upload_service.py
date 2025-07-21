import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict
from gallery.models import PhotoGallery
from gallery.forms import MediaUploadForm
from gallery.services.upload_service import MediaUploadService


@pytest.mark.django_db
def test_service_uploads_image_success(gallery_day):
    image = SimpleUploadedFile("img.png", b"abc", content_type="image/png")
    form = MediaUploadForm(data={}, files=MultiValueDict({"images": [image]}))
    assert form.is_valid()

    service = MediaUploadService(gallery_day, form)
    uploaded = service.upload_images([image])

    assert uploaded == 1
    assert PhotoGallery.objects.count() == 1
    assert not form.errors


@pytest.mark.django_db
def test_service_blocks_upload_if_limit_exceeded(gallery_day, photo_factory):
    for _ in range(5):
        photo_factory(gallery_day=gallery_day)

    image = SimpleUploadedFile("img.png", b"abc", content_type="image/png")
    form = MediaUploadForm(data={}, files=MultiValueDict({"images": [image]}))
    assert form.is_valid()

    service = MediaUploadService(gallery_day, form)
    uploaded = service.upload_images([image])

    assert uploaded == 0
    assert "images" in form.errors
