from django import forms
from .models import PersonalPost, Post


# from user to library
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            "published_date",
            "user",
        )


class PersonalPostForm(forms.ModelForm):
    class Meta:
        model = PersonalPost
        exclude = ("published_date", "user", "date")
        widgets = {
            "content": forms.Textarea(attrs={}),
            "date": forms.DateInput(attrs={"type": "date"}),
        }
