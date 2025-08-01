import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict
from unittest.mock import patch, MagicMock
from gallery.forms import (
    MediaUploadForm,
    validate_image_size,
    validate_video_size,
)


@pytest.fixture
def small_image_file():
    return SimpleUploadedFile("small.png", b"1234", content_type="image/png")


@pytest.fixture
def large_image_file():
    return SimpleUploadedFile(
        "large.png", b"a" * (10 * 1024 * 1024 + 1), content_type="image/png"
    )


@pytest.fixture
def small_video_file():
    return SimpleUploadedFile("video.mp4", b"12345", content_type="video/mp4")


@pytest.fixture
def wrong_ext_video_file():
    return SimpleUploadedFile("video.avi", b"12345", content_type="video/avi")


@pytest.fixture
def large_video_file():
    return SimpleUploadedFile(
        "large.mp4", b"a" * (100 * 1024 * 1024 + 1), content_type="video/mp4"
    )


def test_validate_image_size_passes_small_file(small_image_file):
    validate_image_size(small_image_file)


def test_validate_image_size_fails_large_file(large_image_file):
    with pytest.raises(ValidationError):
        validate_image_size(large_image_file)


def test_validate_video_size_passes_small_file(small_video_file):
    validate_video_size(small_video_file)


def test_validate_video_size_fails_large_file(large_video_file):
    with pytest.raises(ValidationError):
        validate_video_size(large_video_file)


def test_form_handles_empty_files():
    form = MediaUploadForm(files=MultiValueDict({}))
    assert form.is_valid()


@patch("gallery.forms.VideoFileClip")
def test_form_valid_small_files(mock_videoclip, small_image_file, small_video_file):
    mock_clip = MagicMock()
    mock_clip.duration = 10
    mock_videoclip.return_value = mock_clip

    files = MultiValueDict(
        {
            "images": [small_image_file],
            "videos": [small_video_file],
        }
    )
    form = MediaUploadForm(files=files)
    assert form.is_valid()


def test_form_invalid_large_image(large_image_file):
    files = MultiValueDict({"images": [large_image_file]})
    form = MediaUploadForm(files=files)
    assert not form.is_valid()
    assert "images" in form.errors
    assert any("максимальний розмір" in str(e) for e in form.errors["images"])


@patch("gallery.forms.VideoFileClip")
def test_form_invalid_video_duration(mock_videoclip, small_video_file):
    mock_clip = MagicMock()
    mock_clip.duration = 31
    mock_videoclip.return_value = mock_clip

    files = MultiValueDict({"videos": [small_video_file]})
    form = MediaUploadForm(files=files)
    assert not form.is_valid()
    assert "videos" in form.errors
    assert any("довше 30 секунд" in str(e) for e in form.errors["videos"])


def test_form_invalid_large_video(large_video_file):
    files = MultiValueDict({"videos": [large_video_file]})
    form = MediaUploadForm(files=files)
    assert not form.is_valid()
    assert "videos" in form.errors
    assert any("максимальний розмір" in str(e) for e in form.errors["videos"])


def test_form_invalid_video_extension(wrong_ext_video_file):
    files = MultiValueDict({"videos": [wrong_ext_video_file]})
    form = MediaUploadForm(files=files)
    assert not form.is_valid()
    assert "videos" in form.errors
    assert any(
        "Недопустиме розширення" in str(e) or "непідтримуваний формат" in str(e)
        for e in form.errors["videos"]
    )


def test_form_multiple_files_validation(
    small_image_file, large_image_file, small_video_file, large_video_file
):
    files = MultiValueDict(
        {
            "images": [small_image_file, large_image_file],
            "videos": [small_video_file, large_video_file],
        }
    )
    form = MediaUploadForm(files=files)
    is_valid = form.is_valid()
    assert not is_valid
    assert "images" in form.errors
    assert "videos" in form.errors
    assert any("максимальний розмір" in str(e) for e in form.errors["images"])
    assert any("максимальний розмір" in str(e) for e in form.errors["videos"])


@patch("gallery.forms.VideoFileClip")
def test_form_valid_video_duration(mock_videoclip, small_video_file):
    mock_clip = MagicMock()
    mock_clip.duration = 10
    mock_videoclip.return_value = mock_clip

    files = MultiValueDict({"videos": [small_video_file]})
    form = MediaUploadForm(files=files)
    assert form.is_valid()


def test_form_invalid_video_wrong_mime_type():
    wrong_mime_file = SimpleUploadedFile(
        "video.avi", b"12345", content_type="video/avi"
    )
    files = MultiValueDict({"videos": [wrong_mime_file]})
    form = MediaUploadForm(files=files)
    assert not form.is_valid()
    assert "videos" in form.errors
    assert any(
        "Недопустиме розширення" in str(e) or "непідтримуваний формат" in str(e)
        for e in form.errors["videos"]
    )
