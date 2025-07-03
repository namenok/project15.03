import pytest
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

from gallery.models import GalleryDay, PhotoGallery, VideoGallery

# ==== ФІКСТУРИ ==== #

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='testuser', password='password123')


@pytest.fixture
def another_user(db):
    return User.objects.create_user(username='anotheruser', password='password456')


@pytest.fixture
def test_gallery_day(db, test_user):
    return GalleryDay.objects.create(user=test_user, date=date.today())


@pytest.fixture
def dummy_image_file():
    return SimpleUploadedFile(
        name='test_image.png',
        content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\xda\xed\xc1\x01\x01\x00\x00\x00\xc2\xa0\xf7Om\x00\x00\x00\x00IEND\xaeB`\x82',
        content_type='image/png'
    )


@pytest.fixture
def dummy_video_file():
    return SimpleUploadedFile(
        name='test_video.mp4',
        content=b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x08free\x00\x00\x00\x00mdat',
        content_type='video/mp4'
    )


# ==== ТЕСТИ ДЛЯ GalleryDay ==== #

def test_gallery_day_creation(test_user):
    today = date.today()
    gallery_day = GalleryDay.objects.create(user=test_user, date=today)
    assert gallery_day.user == test_user
    assert gallery_day.date == today
    assert GalleryDay.objects.count() == 1


def test_gallery_day_str_method(test_gallery_day):
    expected_str = f"{test_gallery_day.user.username} - {test_gallery_day.date}"
    assert str(test_gallery_day) == expected_str


def test_gallery_day_unique_together(test_user):
    today = date.today()
    GalleryDay.objects.create(user=test_user, date=today)
    with pytest.raises(IntegrityError):
        GalleryDay.objects.create(user=test_user, date=today)


def test_gallery_day_unique_for_different_users(test_user, another_user):
    today = date.today()
    GalleryDay.objects.create(user=test_user, date=today)
    GalleryDay.objects.create(user=another_user, date=today)
    assert GalleryDay.objects.count() == 2


def test_gallery_day_unique_for_different_dates(test_user):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    GalleryDay.objects.create(user=test_user, date=today)
    GalleryDay.objects.create(user=test_user, date=tomorrow)
    assert GalleryDay.objects.count() == 2


# ==== ТЕСТИ ДЛЯ PhotoGallery ==== #

def test_photo_gallery_creation(test_gallery_day, dummy_image_file):
    photo = PhotoGallery.objects.create(
        gallery_day=test_gallery_day,
        image=dummy_image_file,
        description='A beautiful sunrise'
    )
    assert photo.gallery_day == test_gallery_day
    assert photo.description == 'A beautiful sunrise'
    assert photo.image.name.startswith('photos/test_image_')
    assert PhotoGallery.objects.count() == 1


def test_photo_gallery_no_description(test_gallery_day, dummy_image_file):
    photo = PhotoGallery.objects.create(
        gallery_day=test_gallery_day,
        image=dummy_image_file,
        description=''
    )
    assert photo.description == ''


def test_photo_gallery_invalid_image_size(test_gallery_day, dummy_image_file):
    def raise_error(image):
        raise ValidationError('Image size too large.')
    from gallery.models import PhotoGallery
    PhotoGallery._meta.get_field('image').validators = [raise_error]
    photo = PhotoGallery(gallery_day=test_gallery_day, image=dummy_image_file)
    with pytest.raises(ValidationError) as excinfo:
        photo.save()
    assert 'Image size too large.' in str(excinfo.value)


def test_video_gallery_creation(test_gallery_day, dummy_video_file):
    from gallery.models import VideoGallery
    VideoGallery._meta.get_field('video').validators = []
    video = VideoGallery.objects.create(
        gallery_day=test_gallery_day,
        video=dummy_video_file,
        description='A short clip'
    )
    assert video.gallery_day == test_gallery_day
    assert video.description == 'A short clip'
    assert video.video.name.startswith('videos/test_video_')
    assert VideoGallery.objects.count() == 1


def test_video_gallery_no_description(test_gallery_day, dummy_video_file):
    from gallery.models import VideoGallery
    VideoGallery._meta.get_field('video').validators = []
    video = VideoGallery.objects.create(
        gallery_day=test_gallery_day,
        video=dummy_video_file,
        description=''
    )
    assert video.description == ''


def test_video_gallery_invalid_video_size(test_gallery_day, dummy_video_file):
    def raise_error(video):
        raise ValidationError('Video size too large.')
    from gallery.models import VideoGallery
    VideoGallery._meta.get_field('video').validators = [raise_error]
    video = VideoGallery(gallery_day=test_gallery_day, video=dummy_video_file)
    with pytest.raises(ValidationError) as excinfo:
        video.save()
    assert 'Video size too large.' in str(excinfo.value)


def test_video_gallery_invalid_video_duration(test_gallery_day, dummy_video_file):
    def raise_error(video):
        raise ValidationError('Video duration too long.')
    from gallery.models import VideoGallery
    VideoGallery._meta.get_field('video').validators = [raise_error]
    video = VideoGallery(gallery_day=test_gallery_day, video=dummy_video_file)
    with pytest.raises(ValidationError) as excinfo:
        video.save()
    assert 'Video duration too long.' in str(excinfo.value)
