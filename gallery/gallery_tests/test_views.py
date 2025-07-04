import pytest
from datetime import date

from django.urls import reverse
from django.utils import timezone

from gallery.views import get_month_date_range

def test_upload_view_redirects_on_success(client, user, valid_image_file):
    client.force_login(user)
    response = client.post(reverse('gallery:upload'), {
        'images': [valid_image_file],
    }, format='multipart')
    assert response.status_code == 302
    assert response.url == reverse('gallery:gallery')


def test_gallery_view_renders_media(client, user, gallery_day_factory, photo_factory):
    client.force_login(user)
    gallery_day = gallery_day_factory(user=user, date=timezone.localdate())
    photo_factory(gallery_day=gallery_day)  # Create one photo

    response = client.get(reverse('gallery:gallery'))
    assert response.status_code == 200
    assert b'<img' in response.content  # basic check


def test_get_month_date_range():
    today = date(2025, 7, 4)
    first, last = get_month_date_range(today)
    assert first == date(2025, 7, 1)
    assert last == date(2025, 7, 31)
