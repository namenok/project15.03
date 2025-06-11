import mimetypes
import tempfile
from django.core.exceptions import ValidationError
from django.forms import FileField
from django.utils.translation import gettext as gettext
from django.core.exceptions import ValidationError
import io
import os
from django import forms
from moviepy import VideoFileClip
from django import forms
from django.forms.widgets import ClearableFileInput
from django.forms.widgets import FileInput


# 1. Кастомний віджет
class MultiFileInput(FileInput): # CHANGE THIS LINE: Inherit from FileInput
    allow_multiple_selected = True

    # Your value_from_datadict is correct for getting multiple files
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

    )
    videos = MultipleFileField( # Assuming videos uses the same logic
        required=False,
        label="Videos",

    )


def validate_image_size(image):
    max_size = 10 * 1024 * 1024  # 10MB
    if image.size > max_size:
        raise ValidationError(gettext("максимальний розмір фото – 10MB"))

def validate_video_size(video):
    max_size = 100 * 1024 * 1024  # 100MB
    if video.size > max_size:
        raise ValidationError(gettext("максимальний розмір відео – 100MB"))


ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime']
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.mov']

def validate_video_duration(video):
    # Отримуємо розширення файлу в нижньому регістрі
    ext = os.path.splitext(video.name)[1].lower()

    # Визначаємо content_type через mimetypes з урахуванням нижнього регістру імені
    content_type, encoding = mimetypes.guess_type(video.name.lower())

    print(f"DEBUG: video.name={video.name}, content_type={content_type}, extension={ext}")

    # Перевірка розширення файлу
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(gettext("неправильне розширення відеофайлу, має бути .mp4 або .mov"))

    # Перевірка типу файлу (можна опустити цю перевірку, якщо хочеш)
    if content_type not in ALLOWED_VIDEO_TYPES:
        raise ValidationError(gettext("непідтримуваний формат відео, дозволено лише MP4 або MOV"))

    tmp_file_path = None
    try:
        # Створюємо тимчасовий файл для читання відео moviepy
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            for chunk in video.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        clip = VideoFileClip(tmp_file_path)

        if clip.duration > 30:
            raise ValidationError(gettext("нажаль відео не має бути довше 30 секунд"))
    except Exception as e:
        raise ValidationError(gettext("помилка при перевірці відео") + str(e))
    finally:
        if 'clip' in locals():
            clip.close()
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        if hasattr(video, 'seek'):
            video.seek(0)


