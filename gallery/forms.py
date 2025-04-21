from .models import PhotoGallery
from django.forms import ModelForm
from django import forms

class PhotoGalleryForm(ModelForm):
    class Meta:
        model = PhotoGallery
        fields = ['image', 'date', 'description',]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})  # додаємо календарик
        }
