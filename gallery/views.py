from django.shortcuts import render

# Create your views here.
def gallery(request):
    return render(request,'gallery/index.html')


def uploads(request):
    return render(request,'gallery/upload.html')