from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Entry, Foto, Post, Category, LibText, CheckForm, Teg

admin.site.register(Entry)
admin.site.register(Foto)
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(LibText)
admin.site.register(CheckForm)
admin.site.register(Teg)





