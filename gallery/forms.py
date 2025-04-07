from .models import PhotoGallery
from django.forms import ModelForm

class PhotoGalleryForm(ModelForm):
    class Meta:
        model = PhotoGallery
        exclude = ['user']
