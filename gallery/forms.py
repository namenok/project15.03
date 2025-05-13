from django.core.exceptions import ValidationError


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
        help_text="Завантажте до 5 фото"
    )
    videos = MultipleFileField(
        required=False,
        label="Videos",
        help_text="Завантажте до 2 відео"
    )

# для валідації на рівні моделей
def validate_image_size(image):
    max_size = 10 * 1024 * 1024  # 10MB
    if image.size > max_size:
        raise ValidationError("Максимальний розмір фото – 10MB.")

def validate_video_size(video):
    max_size = 100 * 1024 * 1024  # 100MB
    if video.size > max_size:
        raise ValidationError("Максимальний розмір відео – 100MB.")


ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime']
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.mov']

def validate_video_duration(video):
    import mimetypes

    # Визначаємо content_type безпосередньо, якщо відсутній
    content_type = getattr(video, 'content_type', None)
    if content_type is None:
        # Визначаємо тип через mimetypes (наприклад, в admin)
        content_type, _ = mimetypes.guess_type(video.name)

    if content_type not in ALLOWED_VIDEO_TYPES:
        raise ValidationError("Непідтримуваний формат відео. Дозволено лише MP4 або MOV.")

    ext = os.path.splitext(video.name)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError("Неправильне розширення відеофайлу. Має бути .mp4 або .mov.")

    try:
        if hasattr(video, 'read'):
            # це або UploadedFile, або вже відкритий файл
            video_file = io.BytesIO(video.read())
        else:
            # це FieldFile, відкриваємо заново
            with open(video.path, 'rb') as f:
                video_file = io.BytesIO(f.read())

        clip = VideoFileClip(video_file)
        if clip.duration > 30:
            raise ValidationError("Відео повинне бути до 30 секунд.")
    except Exception as e:
        raise ValidationError(f"Помилка при перевірці відео: {e}")
    finally:
        if 'clip' in locals():
            clip.close()
        if hasattr(video, 'seek'):
            video.seek(0)

