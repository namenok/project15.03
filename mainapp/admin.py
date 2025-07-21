from django.contrib import admin

from .models import (
    Category,
    Survey,
    Answers,
    UserAnswer,
    PersonalPost,
    LibText,
    Post,
)


admin.site.register(Category)
admin.site.register(LibText)
admin.site.register(Survey)
admin.site.register(Answers)
admin.site.register(UserAnswer)
admin.site.register(PersonalPost)
admin.site.register(Post)
