from django.contrib import admin
from .models import GalleryDay, PhotoGallery, VideoGallery

admin.site.register(PhotoGallery)
admin.site.register(VideoGallery)
admin.site.register(GalleryDay)
