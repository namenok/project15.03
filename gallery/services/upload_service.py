from django.core.exceptions import ValidationError
from django.utils.translation import gettext as gettext
from gallery.models import PhotoGallery, VideoGallery
from gallery.forms import validate_video_duration, validate_video_size

MAX_IMAGES_PER_DAY = 5
MAX_VIDEOS_PER_DAY = 2

class MediaUploadService:
    def __init__(self, gallery_day, form):
        self.gallery_day = gallery_day
        self.form = form

    def upload_images(self, images):
        existing = self.gallery_day.photos.count()
        available = MAX_IMAGES_PER_DAY - existing
        if available <= 0:
            self.form.add_error("images", gettext("сьогодні вже додано 5 фото"))
            return 0

        to_upload = images[:available]
        success = 0

        for image in to_upload:
            try:
                PhotoGallery.objects.create(gallery_day=self.gallery_day, image=image)
                success += 1
            except ValidationError as e:
                self._add_error("images", e)

        return success

    def upload_videos(self, videos):
        existing = self.gallery_day.videos.count()
        available = MAX_VIDEOS_PER_DAY - existing
        if available <= 0:
            self.form.add_error("videos", gettext("сьогодні вже додано 2 відео"))
            return 0

        to_upload = videos[:available]
        success = 0

        for video in to_upload:
            try:
                validate_video_size(video)
                validate_video_duration(video)
                VideoGallery.objects.create(gallery_day=self.gallery_day, video=video)
                success += 1
            except ValidationError as e:
                self.form.add_error("videos", e)

        return success

    def _add_error(self, field, exception):
        if hasattr(exception, "error_dict") and field in exception.error_dict:
            for err in exception.error_dict[field]:
                self.form.add_error(field, err)
        else:
            self.form.add_error(field, exception)
