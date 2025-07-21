import calendar
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext as gettext

from .forms import (
    MediaUploadForm,
    validate_video_duration,
    validate_video_size,
)
from .models import GalleryDay, PhotoGallery, VideoGallery
from .services.upload_service import MediaUploadService


def get_month_date_range(today):
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return first_day, last_day


def get_media_for_month(user, first_day, last_day):
    gallery_days = GalleryDay.objects.filter(
        user=user, date__gte=first_day, date__lte=last_day
    ).order_by("-date")
    all_photos = []
    all_videos = []
    for gallery_day in gallery_days:
        all_photos.extend(PhotoGallery.objects.filter(gallery_day=gallery_day))
        all_videos.extend(VideoGallery.objects.filter(gallery_day=gallery_day))
    return list(all_photos) + list(all_videos)


def handle_image_uploads(gallery_day, images, form):
    existing_photos_count = gallery_day.photos.count()
    available_image_slots = 5 - existing_photos_count
    if available_image_slots <= 0:
        form.add_error("images", gettext("сьогодні вже додано 5 фото"))
        return 0
    images_to_upload = images[:available_image_slots]
    image_upload_success = 0
    for image in images_to_upload:
        try:
            PhotoGallery.objects.create(gallery_day=gallery_day, image=image)
            image_upload_success += 1
        except ValidationError as e:
            if hasattr(e, "error_dict") and "image" in e.error_dict:
                for err in e.error_dict["image"]:
                    form.add_error("images", err)
            else:
                form.add_error("images", e)
    return image_upload_success


def handle_video_uploads(gallery_day, videos, form):
    existing_videos_count = gallery_day.videos.count()
    available_video_slots = 2 - existing_videos_count
    if available_video_slots <= 0:
        form.add_error("videos", gettext("сьогодні вже додано 2 відео"))
        return 0
    videos_to_upload = videos[:available_video_slots]
    video_upload_success = 0
    for video in videos_to_upload:
        try:
            validate_video_size(video)
            validate_video_duration(video)
            VideoGallery.objects.create(gallery_day=gallery_day, video=video)
            video_upload_success += 1
        except ValidationError as e:
            form.add_error("videos", e)
    return video_upload_success


@login_required()
def gallery(request):
    today = timezone.localdate()

    first_day_of_month, last_day_of_month = get_month_date_range(today)

    media_items = get_media_for_month(
        request.user, first_day_of_month, last_day_of_month
    )

    return render(request, "gallery/index.html", {"media_items": media_items})


@login_required()
def upload(request):
    if request.method == "POST":
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_day, _ = GalleryDay.objects.get_or_create(
                user=request.user, date=date.today()
            )
            service = MediaUploadService(gallery_day, form)
            service.upload_images(request.FILES.getlist("images"))
            service.upload_videos(request.FILES.getlist("videos"))

            if not form.errors:
                messages.success(request, gettext("файли успішно завантажено"))
                return redirect("gallery:gallery")
            else:
                messages.error(
                    request, gettext("виникли помилки під час завантаження файлів")
                )
    else:
        form = MediaUploadForm()

    return render(request, "gallery/upload.html", {"form": form})
