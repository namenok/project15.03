import mimetypes
import tempfile

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError
import io
import os
from django import forms
from moviepy import VideoFileClip

from django import forms
from django.forms.widgets import ClearableFileInput


# 1. Кастомний віджет
class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True  # ключове!

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)


# 2. Кастомне поле
class MultipleFileField(forms.FileField):
    widget = MultiFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        return data


# 3. Форма
class MediaUploadForm(forms.Form):
    images = MultipleFileField(
        required=False,
        label="Images",
        help_text=_("Завантажте до 5 фото"),
    )
    videos = MultipleFileField(
        required=False,
        label="Videos",
        help_text=_("Завантажте до 2 відео"),
    )


def validate_image_size(image):
    max_size = 10 * 1024 * 1024  # 10MB
    if image.size > max_size:
        raise ValidationError(_("Максимальний розмір фото – 10MB."))

def validate_video_size(video):
    max_size = 100 * 1024 * 1024  # 100MB
    if video.size > max_size:
        raise ValidationError(_("Максимальний розмір відео – 100MB."))


ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime']
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.mov']

def validate_video_duration(video):
    content_type = getattr(video, 'content_type', None)
    if content_type is None:
        content_type, _ = mimetypes.guess_type(video.name)

    if content_type not in ALLOWED_VIDEO_TYPES:
        raise ValidationError(_("Непідтримуваний формат відео. Дозволено лише MP4 або MOV."))

    ext = os.path.splitext(video.name)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(_("Неправильне розширення відеофайлу. Має бути .mp4 або .mov."))

    tmp_file_path = None  # 👉 обов’язково ініціалізуємо
    try:
        # Створюємо тимчасовий файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            for chunk in video.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        clip = VideoFileClip(tmp_file_path)

        if clip.duration > 30:
            raise ValidationError(_("Відео повинне бути до 30 секунд."))
    except Exception as e:
        raise ValidationError(_("Помилка при перевірці відео: %(error)s") % {"error": e})
    finally:
        if 'clip' in locals():
            clip.close()
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        if hasattr(video, 'seek'):
            video.seek(0)

