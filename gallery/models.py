from django.contrib.auth.models import User
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os

from moviepy import VideoFileClip

from gallery.forms import validate_video_duration, validate_image_size, validate_video_size





class GalleryDay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'date')  # Один запис на день на користувача

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class PhotoGallery(models.Model):
    gallery_day = models.ForeignKey(GalleryDay, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/', validators=[validate_image_size])
    description = models.CharField(max_length=100, blank=True)

    def clean(self):
        if self.gallery_day.photos.count() >= 5:
            raise ValidationError(_("На день можна додати лише 5 фото."))


class VideoGallery(models.Model):
    gallery_day = models.ForeignKey(GalleryDay, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='videos/', validators=[validate_video_size])
    description = models.CharField(max_length=100, blank=True)
    def clean(self):
        if self.gallery_day.videos.count() >= 2:
            raise ValidationError(_("На день можна додати лише 2 відео."))

