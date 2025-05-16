from django.contrib import admin
from .models import PhotoGallery, VideoGallery, GalleryDay
# Register your models here.
admin.site.register(PhotoGallery)
admin.site.register(VideoGallery)
admin.site.register(GalleryDay)
