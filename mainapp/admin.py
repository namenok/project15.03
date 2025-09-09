from django.contrib import admin

from .models import (
    Survey,
    Answers,
    UserAnswer,
    PersonalPost,

)


admin.site.register(Survey)
admin.site.register(Answers)
admin.site.register(UserAnswer)
admin.site.register(PersonalPost)

