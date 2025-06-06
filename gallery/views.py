from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.utils.translation import gettext as gettext
from .models import PhotoGallery, VideoGallery, GalleryDay
from .forms import  validate_image_size, MediaUploadForm, validate_video_size, validate_video_duration


@login_required()
def gallery(request):
    # Отримуємо день, коли були завантажені медіа файли
    gallery_day = GalleryDay.objects.filter(user=request.user).order_by('-date').first()
    # Отримуємо фото та відео для цього дня
    photos = PhotoGallery.objects.filter(gallery_day=gallery_day)
    videos = VideoGallery.objects.filter(gallery_day=gallery_day)
    # Об'єднуємо фото та відео в один список (за бажанням можна їх відображати окремо)
    media_items = list(photos) + list(videos)
    return render(request, 'gallery/index.html', {'media_items': media_items})


@login_required()
def upload(request):
    if request.method == "POST":
        form = MediaUploadForm(request.POST, request.FILES)
        # getlist обов'язково — бо в MultipleFileField передається список файлів
        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')
        images = images[:5]
        if form.is_valid():
            gallery_day, created = GalleryDay.objects.get_or_create(
                user=request.user,
                date=date.today()
            )
            # Додаємо фотки
            for image in images:
                try:
                    validate_image_size(image)
                    PhotoGallery.objects.create(gallery_day=gallery_day, image=image)
                except ValidationError as e:
                    form.add_error('images', e)
            # Перевірка кількості відео вже в базі
            existing_videos = gallery_day.videos.count()
            available_video_slots = 2 - existing_videos
            if available_video_slots <= 0:
                form.add_error('videos', gettext("На сьогодні вже додано 2 відео."))
            else:
                # Обмежуємо кількість відео для завантаження
                videos = videos[:available_video_slots]
                for video in videos:
                    try:
                        validate_video_size(video)
                        validate_video_duration(video)
                        VideoGallery.objects.create(gallery_day=gallery_day, video=video)
                    except ValidationError as e:
                        form.add_error('videos', e)
            if not form.errors:
                messages.success(request, gettext("Файли успішно завантажено."))
                return redirect('gallery:gallery')
    else:
        form = MediaUploadForm()
    return render(request, 'gallery/upload.html', {'form': form})