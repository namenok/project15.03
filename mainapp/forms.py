from django import forms
from .models import PersonalPost, Post
from django.utils.translation import gettext_lazy as _


# від юзера в бібліотеку
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            "published_date",
            "user",
        )


# персональний юзера в його щоденник
class PersonalPostForm(forms.ModelForm):
    class Meta:
        model = PersonalPost
        exclude = ("published_date", "user", "date")
        widgets = {
            "content": forms.Textarea(
                attrs={"placeholder": _("пиши свій пост на сьогодні...")}
            ),
            "date": forms.DateInput(attrs={"type": "date"}),
        }
