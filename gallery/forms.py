import mimetypes
import os
import tempfile

from django import forms
from django.core.exceptions import ValidationError

from django.forms.widgets import FileInput
from django.utils.translation import gettext as gettext
from moviepy import VideoFileClip


class MultiFileInput(FileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)


class MultipleFileField(forms.FileField):
    widget = MultiFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        return data


class MediaUploadForm(forms.Form):
    images = MultipleFileField(required=False, label="Images")
    videos = MultipleFileField(required=False, label="Videos")

    def clean_images(self):
        images = self.cleaned_data.get("images", [])
        errors = []
        for img in images:
            try:
                validate_image_size(img)
            except ValidationError as e:
                errors.append(e)
        if errors:
            raise ValidationError(errors)
        return images

    def clean_videos(self):
        videos = self.cleaned_data.get("videos", [])
        errors = []
        for vid in videos:
            try:
                validate_video_size(vid)
                validate_video_duration(vid)
            except ValidationError as e:
                errors.append(e)
        if errors:
            raise ValidationError(errors)
        return videos


def validate_image_size(image):
    max_size = 10 * 1024 * 1024  # 10MB

    size = getattr(image, "size", None)
    if size is None and hasattr(image, "file"):
        size = getattr(image.file, "size", None)

    if size is None and hasattr(image, "tell") and hasattr(image, "seek"):
        pos = image.tell()
        image.seek(0, 2)
        size = image.tell()
        image.seek(pos)

    print(f"DEBUG validate_image_size: {getattr(image, 'name', '')} — {size} байт")

    if size is not None:
        if size > max_size:
            raise ValidationError(gettext("максимальний розмір фото – 10MB"))
    else:
        raise ValidationError(gettext("Не вдалося визначити розмір файлу."))


def validate_video_size(video):
    max_size = 100 * 1024 * 1024  # 100MB
    if hasattr(video, "size"):
        if video.size > max_size:
            raise ValidationError(gettext("максимальний розмір відео – 100MB"))
    else:
        raise ValidationError(gettext("Не вдалося визначити розмір файлу."))


ALLOWED_VIDEO_TYPES = ["video/mp4", "video/quicktime"]
ALLOWED_VIDEO_EXTENSIONS = [".mp4", ".mov"]


def validate_video_duration(video):
    ext = os.path.splitext(video.name)[1].lower()

    content_type, encoding = mimetypes.guess_type(video.name.lower())

    print(
        f"DEBUG: video.name={video.name}, content_type={content_type}, extension={ext}"
    )

    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            {
                "videos": [
                    gettext("неправильне розширення відеофайлу, має бути .mp4 або .mov")
                ]
            }
        )

    if content_type not in ALLOWED_VIDEO_TYPES:
        raise ValidationError(
            {
                "videos": [
                    gettext("непідтримуваний формат відео, дозволено лише MP4 або MOV")
                ]
            }
        )

    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            for chunk in video.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        clip = VideoFileClip(tmp_file_path)

        if clip.duration > 30:
            raise ValidationError(
                {"videos": [gettext("нажаль відео не має бути довше 30 секунд")]}
            )
    except Exception as e:
        raise ValidationError(
            {"videos": [gettext("помилка при перевірці відео") + str(e)]}
        )
    finally:
        if "clip" in locals():
            clip.close()
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        if hasattr(video, "seek"):
            video.seek(0)
