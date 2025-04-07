from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class PhotoGallery(models.Model):

    image = models.ImageField(upload_to='uploads')
    description = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="Автор")
    date = models.DateField()

    def __str__(self):
        return self.description