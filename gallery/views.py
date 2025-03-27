from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import PhotoGallery
from .forms import PhotoGalleryForm
# Create your views here.



@login_required()
def gallery(request):
    photos = PhotoGallery.objects.all()
    return render(request,'gallery/index.html', {'photos': photos})



@login_required()
def upload(request):
    if request.method == "POST":
        form = PhotoGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return(gallery(request))
    form = PhotoGalleryForm()
    return render(request,'gallery/upload.html', {'form': form})