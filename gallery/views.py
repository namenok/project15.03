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

    # Визначаємо перший день поточного місяця
    first_day_of_month = today.replace(day=1)

    # Визначаємо останній день поточного місяця
    # calendar.monthrange повертає кортеж (день тижня першого дня, кількість днів у місяці)
    last_day_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    # Отримуємо всі GalleryDay об'єкти для поточного користувача за поточний місяць
    # Ми фільтруємо за діапазоном дат: від першого дня місяця до останнього
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

    # Об'єднуємо фото та відео в один список.
    # За бажанням, ви можете їх відображати окремо в шаблоні.
    media_items = list(all_photos_for_month) + list(all_videos_for_month)

    # Можливо, ви захочете відсортувати media_items за датою створення або завантаження,
    # якщо об'єднали їх. Для цього потрібно додати поле 'created_at' або 'uploaded_at'
    # до моделей PhotoGallery та VideoGallery.
    # Наприклад, якщо додати 'uploaded_at = models.DateTimeField(auto_now_add=True)'
    # до обох моделей, тоді можна сортувати так:
    # media_items.sort(key=lambda item: item.uploaded_at, reverse=True)
    return render(request, 'gallery/index.html', {'media_items': media_items})


@login_required()
def upload(request):
    if request.method == "POST":
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():  # Validate form fields first
            # Get the GalleryDay object for today for the current user
            gallery_day, created = GalleryDay.objects.get_or_create(
                user=request.user,
                date=date.today()
            )

            # --- Validation for Images (Crucial Part) ---
            images_to_upload = request.FILES.getlist('images')
            existing_photos_count = gallery_day.photos.count()  # Get existing count *before* adding new ones

            # Filter new images to only upload up to the limit
            # This ensures we don't try to save more than allowed
            available_image_slots = 5 - existing_photos_count
            if available_image_slots <= 0:
                form.add_error('images', gettext("сьогодні вже додано 5 фото"))
                images_to_upload = []  # Prevent processing any images if already at limit
            else:
                images_to_upload = images_to_upload[:available_image_slots]  # Limit new uploads

            # Process images
            image_upload_success = 0
            for image in images_to_upload:
                try:
                    validate_image_size(image)  # Validate size before creating
                    PhotoGallery.objects.create(gallery_day=gallery_day, image=image)
                    image_upload_success += 1
                except ValidationError as e:
                    form.add_error('images', e)

            # Add a message if some images were skipped due to limit or errors
            if images_to_upload and image_upload_success < len(images_to_upload):
                # This catches if some files in the selection were over size, etc.
                # Or if they tried to upload more than available_image_slots
                pass  # Specific error messages are already added by form.add_error

            # --- Validation for Videos (Your Existing Logic, good) ---
            videos_to_upload = request.FILES.getlist('videos')
            existing_videos_count = gallery_day.videos.count()
            available_video_slots = 2 - existing_videos_count

            if available_video_slots <= 0:
                form.add_error('videos', gettext("сьогодні вже додано 2 відео"))
                videos_to_upload = []  # Prevent processing any videos if already at limit
            else:
                videos_to_upload = videos_to_upload[:available_video_slots]  # Limit new uploads

            # Process videos
            for video in videos_to_upload:
                try:
                    validate_video_size(video)
                    validate_video_duration(video)
                    VideoGallery.objects.create(gallery_day=gallery_day, video=video)
                except ValidationError as e:
                    form.add_error('videos', e)

            # --- Final Check and Redirect ---
            # Only show success message and redirect if there are NO form errors after processing
            if not form.errors:
                messages.success(request, gettext("файли успішно завантажено"))
                return redirect('gallery:gallery')
            else:
                # If there are errors, messages.error might be useful too
                messages.error(request, gettext("виникли помилки під час завантаження файлів"))

    else:  # GET request
        form = MediaUploadForm()

    return render(request, 'gallery/upload.html', {'form': form})