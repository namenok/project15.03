import pytest
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from unittest.mock import patch  # Для імітації файлів та зовнішніх функцій

# Імпортуємо ваші моделі
from ..models import GalleryDay, PhotoGallery, VideoGallery


# Імпортуємо ваші валідатори, якщо вони використовуються напряму в тестах,
# або якщо ви хочете перевірити їх окремо.
# Наразі ми зосередимося на поведінці моделі.
# from ..forms import validate_video_duration, validate_image_size, validate_video_size

# --- Pytest Fixtures ---
# Фікстури створюють дані для тестів і гарантують чисту базу даних для кожного тесту.

@pytest.fixture
def test_user(db):
    """Фікстура для створення тестового користувача."""
    return User.objects.create_user(username='testuser', password='password123')


@pytest.fixture
def another_user(db):
    """Фікстура для створення іншого тестового користувача."""
    return User.objects.create_user(username='anotheruser', password='password456')


@pytest.fixture
def test_gallery_day(db, test_user):
    """Фікстура для створення тестового GalleryDay."""
    return GalleryDay.objects.create(user=test_user, date=date.today())


# --- Тести для GalleryDay ---

def test_gallery_day_creation(test_user):
    """Перевіряє успішне створення об'єкта GalleryDay."""
    today = date.today()
    gallery_day = GalleryDay.objects.create(user=test_user, date=today)
    assert gallery_day.user == test_user
    assert gallery_day.date == today
    assert GalleryDay.objects.count() == 1


def test_gallery_day_str_method(test_gallery_day):
    """Перевіряє коректність методу __str__ для GalleryDay."""
    expected_str = f"{test_gallery_day.user.username} - {test_gallery_day.date}"
    assert str(test_gallery_day) == expected_str


def test_gallery_day_unique_together(test_user):
    """
    Перевіряє, що не можна створити два GalleryDay для одного користувача на одну дату.
    Використовуємо pytest.raises для перевірки очікуваної помилки.
    """
    today = date.today()
    GalleryDay.objects.create(user=test_user, date=today)  # Створюємо перший об'єкт
    with pytest.raises(IntegrityError):  # Очікуємо IntegrityError
        GalleryDay.objects.create(user=test_user, date=today)  # Намагаємося створити дублікат


def test_gallery_day_unique_for_different_users(test_user, another_user):
    """
    Перевіряє, що різні користувачі можуть мати GalleryDay на одну дату.
    """
    today = date.today()
    GalleryDay.objects.create(user=test_user, date=today)
    GalleryDay.objects.create(user=another_user, date=today)  # Інший користувач на ту саму дату
    assert GalleryDay.objects.count() == 2  # Обидва мають бути створені


def test_gallery_day_unique_for_different_dates(test_user):
    """
    Перевіряє, що один користувач може мати GalleryDay на різні дати.
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)
    GalleryDay.objects.create(user=test_user, date=today)
    GalleryDay.objects.create(user=test_user, date=tomorrow)  # Та сама користувач на іншу дату
    assert GalleryDay.objects.count() == 2


# --- Тести для PhotoGallery та VideoGallery ---
# Для цих моделей нам потрібно імітувати файли, оскільки
# Django не може просто так завантажити файли без повного тестового оточення.
# Ми будемо використовувати `unittest.mock.patch` та `SimpleUploadedFile`.

from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def dummy_image_file():
    """Створює імітований (фіктивний) файл зображення."""
    # Це реальні байти дуже маленького PNG, щоб імітувати реальний файл
    return SimpleUploadedFile(
        name='test_image.png',
        content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\xda\xed\xc1\x01\x01\x00\x00\x00\xc2\xa0\xf7Om\x00\x00\x00\x00IEND\xaeB`\x82',
        content_type='image/png'
    )


@pytest.fixture
def dummy_video_file():
    """Створює імітований (фіктивний) файл відео (дуже маленький MP4)."""
    # Це мінімальні байти для MP4, щоб імітувати файл.
    # Для реальної перевірки тривалості/розміру знадобиться більше мокувань.
    return SimpleUploadedFile(
        name='test_video.mp4',
        content=b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x08free\x00\x00\x00\x00mdat',
        content_type='video/mp4'
    )


# Оскільки `validate_video_duration` використовує `moviepy`,
# ми повинні мокувати (імітувати) його поведінку, щоб уникнути
# необхідності реального встановлення `moviepy` та обробки файлів під час тестів.

# Це важливий крок:
# Ми замінюємо оригінальну функцію validate_video_duration
# на "підроблену" (mock), яка завжди повертає True або False
# залежно від сценарію тесту, без реального аналізу відео.
# Те саме стосується validate_image_size та validate_video_size,
# якщо вони виконують реальну перевірку файлу.

# Виносимо patcher до фікстур, щоб він застосовувався до тестів:
@pytest.fixture(autouse=True)  # `autouse=True` означає, що ця фікстура буде застосована до всіх тестів
def mock_validators():
    """Мокує функції валідаторів з forms.py, щоб уникнути роботи з реальними файлами."""
    with patch('gallery.forms.validate_image_size') as mock_img_size, \
            patch('gallery.forms.validate_video_size') as mock_vid_size, \
            patch('gallery.forms.validate_video_duration') as mock_vid_duration:
        # За замовчуванням, моки роблять вигляд, що все OK.
        # Ви можете змінити їхню поведінку для певних тестів,
        # щоб імітувати помилку валідації.
        mock_img_size.return_value = None  # None означає, що валідація пройшла без помилок
        mock_vid_size.return_value = None
        mock_vid_duration.return_value = None

        yield  # Код після yield виконується після тесту


# --- Тести для PhotoGallery ---

def test_photo_gallery_creation(test_gallery_day, dummy_image_file):
    """Перевіряє успішне створення об'єкта PhotoGallery."""
    photo = PhotoGallery.objects.create(
        gallery_day=test_gallery_day,
        image=dummy_image_file,
        description='A beautiful sunrise'
    )
    assert photo.gallery_day == test_gallery_day
    assert photo.description == 'A beautiful sunrise'
    assert 'test_image.png' in photo.image.name  # Перевіряємо, що ім'я файлу збережено
    assert PhotoGallery.objects.count() == 1


def test_photo_gallery_no_description(test_gallery_day, dummy_image_file):
    """Перевіряє створення PhotoGallery без опису."""
    photo = PhotoGallery.objects.create(
        gallery_day=test_gallery_day,
        image=dummy_image_file,
        description=''  # Порожній опис дозволено
    )
    assert photo.description == ''


# Приклад тесту на ВАЛІДАЦІЮ (якщо валідаторів немає в моделі напряму, це може бути в формах)
# Цей тест перевіряє, чи модель PhotoGallery відхилить зображення,
# якщо mock_image_size (який імітує ваш валідатор) поверне ValidationError.
@patch('gallery.forms.validate_image_size')  # Мокуємо тільки цей валідатор для цього тесту
def test_photo_gallery_invalid_image_size(mock_validate_image_size, test_gallery_day, dummy_image_file):
    """Перевіряє, що PhotoGallery відхиляє зображення з невірним розміром."""
    # Налаштовуємо mock_validate_image_size так, щоб він викликав помилку валідації
    mock_validate_image_size.side_effect = ValidationError('Image size too large.')

    with pytest.raises(ValidationError) as excinfo:
        PhotoGallery.objects.create(
            gallery_day=test_gallery_day,
            image=dummy_image_file,
            description='Too big'
        )
    assert 'Image size too large.' in str(excinfo.value)


# --- Тести для VideoGallery ---

def test_video_gallery_creation(test_gallery_day, dummy_video_file):
    """Перевіряє успішне створення об'єкта VideoGallery."""
    video_entry = VideoGallery.objects.create(
        gallery_day=test_gallery_day,
        video=dummy_video_file,
        description='A short clip'
    )
    assert video_entry.gallery_day == test_gallery_day
    assert video_entry.description == 'A short clip'
    assert 'test_video.mp4' in video_entry.video.name
    assert VideoGallery.objects.count() == 1


def test_video_gallery_no_description(test_gallery_day, dummy_video_file):
    """Перевіряє створення VideoGallery без опису."""
    video_entry = VideoGallery.objects.create(
        gallery_day=test_gallery_day,
        video=dummy_video_file,
        description=''
    )
    assert video_entry.description == ''


@patch('gallery.forms.validate_video_size')
def test_video_gallery_invalid_video_size(mock_validate_video_size, test_gallery_day, dummy_video_file):
    """Перевіряє, що VideoGallery відхиляє відео з невірним розміром."""
    mock_validate_video_size.side_effect = ValidationError('Video size too large.')

    with pytest.raises(ValidationError) as excinfo:
        VideoGallery.objects.create(
            gallery_day=test_gallery_day,
            video=dummy_video_file,
            description='Too big video'
        )
    assert 'Video size too large.' in str(excinfo.value)


@patch('gallery.forms.validate_video_duration')
def test_video_gallery_invalid_video_duration(mock_validate_video_duration, test_gallery_day, dummy_video_file):
    """Перевіряє, що VideoGallery відхиляє відео з невірною тривалістю."""
    mock_validate_video_duration.side_effect = ValidationError('Video duration too long.')

    with pytest.raises(ValidationError) as excinfo:
        VideoGallery.objects.create(
            gallery_day=test_gallery_day,
            video=dummy_video_file,
            description='Too long video'
        )
    assert 'Video duration too long.' in str(excinfo.value)

# Примітка: тестування `validate_video_duration` вимагає, щоб `moviepy` був встановлений
# або щоб ви мокували `VideoFileClip`. У цьому прикладі ми використовуємо `patch`
# для імітації поведінки валідаторів, щоб уникнути реальних операцій з файлами та moviepy.
# Якщо ви хочете протестувати самі валідатори, вам доведеться тестувати їх окремо
# та надавати їм реальні або імітовані файли, які вони можуть обробити.