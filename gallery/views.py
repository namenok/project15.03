from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.utils.translation import gettext as gettext
from .models import PhotoGallery, VideoGallery, GalleryDay
from .forms import  validate_image_size, MediaUploadForm, validate_video_size, validate_video_duration
from django.utils import timezone
import calendar

@login_required()
def gallery(request):
    # Отримуємо поточну дату
    today = timezone.localdate() # Використовуємо timezone.localdate() для поточної дати з урахуванням локального часового поясу

    first_day_of_month = today.replace(day=1)

    last_day_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    gallery_days_for_month = GalleryDay.objects.filter(
        user=request.user,
        date__gte=first_day_of_month, # Дата більша або дорівнює першому дню місяця
        date__lte=last_day_of_month    # Дата менша або дорівнює останньому дню місяця
    ).order_by('-date') # Сортуємо за датою у спадному порядку, якщо потрібно

    # Ініціалізуємо порожні списки для фото та відео
    all_photos_for_month = []
    all_videos_for_month = []

    # Перебираємо кожен GalleryDay за поточний місяць і збираємо всі фото та відео
    for gallery_day in gallery_days_for_month:
        all_photos_for_month.extend(PhotoGallery.objects.filter(gallery_day=gallery_day))
        all_videos_for_month.extend(VideoGallery.objects.filter(gallery_day=gallery_day))

    media_items = list(all_photos_for_month) + list(all_videos_for_month)

    return render(request, 'gallery/index.html', {'media_items': media_items})



@login_required()
def upload(request):
    if request.method == "POST":
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_day, _ = GalleryDay.objects.get_or_create(
                user=request.user,
                date=date.today()
            )

            # Images
            images_to_upload = request.FILES.getlist('images')
            existing_photos_count = gallery_day.photos.count()
            available_image_slots = 5 - existing_photos_count
            if available_image_slots <= 0:
                form.add_error('images', gettext("сьогодні вже додано 5 фото"))
                images_to_upload = []
            else:
                images_to_upload = images_to_upload[:available_image_slots]

            image_upload_success = 0
            for image in images_to_upload:
                try:

                    PhotoGallery.objects.create(gallery_day=gallery_day, image=image)
                    image_upload_success += 1
                except ValidationError as e:
                    # If the error is for the model field 'image', map it to the form field 'images'
                    if hasattr(e, "error_dict") and "image" in e.error_dict:
                        for err in e.error_dict["image"]:
                            form.add_error("images", err)
                    else:
                        form.add_error("images", e)

            # Videos
            videos_to_upload = request.FILES.getlist('videos')
            existing_videos_count = gallery_day.videos.count()
            available_video_slots = 2 - existing_videos_count
            if available_video_slots <= 0:
                form.add_error('videos', gettext("сьогодні вже додано 2 відео"))
                videos_to_upload = []
            else:
                videos_to_upload = videos_to_upload[:available_video_slots]

            for video in videos_to_upload:
                try:
                    validate_video_size(video)
                    validate_video_duration(video)
                    VideoGallery.objects.create(gallery_day=gallery_day, video=video)
                except ValidationError as e:
                    form.add_error('videos', e)

            # Final check
            if not form.errors:
                messages.success(request, gettext("файли успішно завантажено"))
                return redirect('gallery:gallery')
            else:
                messages.error(request, gettext("виникли помилки під час завантаження файлів"))
    else:
        form = MediaUploadForm()

    return render(request, 'gallery/upload.html', {'form': form})