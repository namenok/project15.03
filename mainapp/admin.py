from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import  Category, Teg, Survey, Answers, UserAnswer, PersonalPost, LibText, Post

# admin.site.register(Entry)
#
# admin.site.register(Foto)

admin.site.register(Category)

admin.site.register(LibText)
# admin.site.register(CheckForm)

admin.site.register(Teg)

admin.site.register(Survey)
admin.site.register(Answers)
admin.site.register(UserAnswer)

admin.site.register(PersonalPost)

admin.site.register(Post)






