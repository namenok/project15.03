import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict
from unittest.mock import patch, MagicMock
from gallery.forms import (
    MediaUploadForm,
    validate_image_size,
    validate_video_size,
    validate_video_duration,
)


@pytest.fixture
def small_image_file():
    return SimpleUploadedFile('small.png', b'1234', content_type='image/png')


@pytest.fixture
def large_image_file():
    return SimpleUploadedFile('large.png', b'a' * (10 * 1024 * 1024 + 1), content_type='image/png')  # 10MB + 1 byte


@pytest.fixture
def small_video_file():
    return SimpleUploadedFile('video.mp4', b'12345', content_type='video/mp4')


@pytest.fixture
def wrong_ext_video_file():
    return SimpleUploadedFile('video.avi', b'12345', content_type='video/avi')


@pytest.fixture
def large_video_file():
    return SimpleUploadedFile('large.mp4', b'a' * (100 * 1024 * 1024 + 1), content_type='video/mp4')  # 100MB + 1 byte


def test_validate_video_size_passes_small_file(small_video_file):
    validate_video_size(small_video_file)  # should not raise


def test_validate_video_size_fails_large_file(large_video_file):
    with pytest.raises(ValidationError):
        validate_video_size(large_video_file)


def test_validate_image_size_passes_small_file():
    small_file = SimpleUploadedFile('small.png', b'1234')
    validate_image_size(small_file)  # should not raise


def test_validate_image_size_fails_large_file():
    large_content = b'a' * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
    large_file = SimpleUploadedFile('large.png', large_content)
    with pytest.raises(ValidationError):
        validate_image_size(large_file)


def test_form_handles_empty_files():
    form = MediaUploadForm(files=MultiValueDict({}))
    assert form.is_valid()  # no files should be valid


@patch('gallery.forms.VideoFileClip')
def test_form_valid_small_files(mock_videoclip, small_image_file, small_video_file):
    mock_clip = MagicMock()
    mock_clip.duration = 10  # valid duration within limits
    mock_videoclip.return_value = mock_clip

    files = MultiValueDict({
        'images': [small_image_file],
        'videos': [small_video_file],
    })
    form = MediaUploadForm(files=files)
    if not form.is_valid():
        print("Form errors:", form.errors)  # Debug output
    assert form.is_valid()


def test_form_invalid_large_image(large_image_file):
    files = MultiValueDict({'images': [large_image_file]})
    form = MediaUploadForm(files=files)
    assert not form.is_valid()
    assert 'images' in form.errors


def test_form_invalid_large_image_via_form(large_image_file):
    files = MultiValueDict({'images': [large_image_file]})
    form = MediaUploadForm(files=files)
    assert not form.is_valid()
    assert 'images' in form.errors


@patch('gallery.forms.VideoFileClip')
def test_form_invalid_video_duration_via_form(mock_videoclip, small_video_file):
    mock_clip = MagicMock()
    mock_clip.duration = 31  # invalid duration > 30 sec
    mock_videoclip.return_value = mock_clip

    files = MultiValueDict({'videos': [small_video_file]})
    form = MediaUploadForm(files=files)
    assert not form.is_valid()
    assert 'videos' in form.errors


def test_form_invalid_large_video(large_video_file):
    files = MultiValueDict({'videos': [large_video_file]})
    form = MediaUploadForm(files=files)
    # Directly testing validator here; form validation uses it internally as well
    with pytest.raises(ValidationError):
        for video in form.files.getlist('videos'):
            validate_video_size(video)


def test_form_invalid_video_extension(wrong_ext_video_file):
    files = MultiValueDict({'videos': [wrong_ext_video_file]})
    form = MediaUploadForm(files=files)
    with pytest.raises(ValidationError):
        validate_video_duration(wrong_ext_video_file)


@patch('gallery.forms.VideoFileClip')
def test_form_valid_video_duration(mock_videoclip, small_video_file):
    mock_clip = MagicMock()
    mock_clip.duration = 10
    mock_videoclip.return_value = mock_clip

    files = MultiValueDict({'videos': [small_video_file]})
    form = MediaUploadForm(files=files)
    validate_video_duration(small_video_file)  # Should pass without exception


@patch('gallery.forms.VideoFileClip')
def test_form_invalid_video_duration(mock_videoclip, small_video_file):
    mock_clip = MagicMock()
    mock_clip.duration = 31
    mock_videoclip.return_value = mock_clip

    files = MultiValueDict({'videos': [small_video_file]})
    form = MediaUploadForm(files=files)
    with pytest.raises(ValidationError):
        validate_video_duration(small_video_file)


def test_form_multiple_files_validation(small_image_file, large_image_file, small_video_file, large_video_file):
    files = MultiValueDict({
        'images': [small_image_file, large_image_file],
        'videos': [small_video_file, large_video_file],
    })
    form = MediaUploadForm(files=files)
    is_valid = form.is_valid()
    if not is_valid:
        print("Form errors:", form.errors)  # Debug output
    assert not is_valid
    assert 'images' in form.errors
    assert 'videos' in form.errors
    assert any("максимальний розмір" in str(err) for err in form.errors['images'])
    assert any("максимальний розмір" in str(err) for err in form.errors['videos'])


def test_form_invalid_video_wrong_mime_type():
    wrong_mime_file = SimpleUploadedFile('video.avi', b'12345', content_type='video/avi')  # note extension .avi
    files = MultiValueDict({'videos': [wrong_mime_file]})
    form = MediaUploadForm(files=files)
    is_valid = form.is_valid()
    if is_valid:
        print("Form unexpectedly valid")
    else:
        print("Form errors:", form.errors)
    assert not is_valid
    assert 'videos' in form.errors
    assert any("неправильне розширення" in str(err) or "непідтримуваний формат" in str(err) for err in form.errors['videos'])


def test_form_invalid_large_image_error_message(large_image_file):
    files = MultiValueDict({'images': [large_image_file]})
    form = MediaUploadForm(files=files)
    form.is_valid()
    assert 'images' in form.errors
    error_msgs = form.errors['images']
    assert any("максимальний розмір" in str(msg) for msg in error_msgs)


@patch('gallery.forms.VideoFileClip')
def test_form_invalid_video_duration_error_message(mock_videoclip, small_video_file):
    mock_clip = MagicMock()
    mock_clip.duration = 31
    mock_videoclip.return_value = mock_clip

    files = MultiValueDict({'videos': [small_video_file]})
    form = MediaUploadForm(files=files)
    form.is_valid()
    assert 'videos' in form.errors
    error_msgs = form.errors['videos']
    assert any("довше 30 секунд" in str(msg) for msg in error_msgs)
