from django import forms

from .models import PersonalPost, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('published_date',  )



class PersonalPostForm(forms.ModelForm):
    class Meta:
        model = PersonalPost
        exclude = ('published_date', 'user', )
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Напиши свій пост на сьогодні...'}),
            'date': forms.DateInput(attrs={'type': 'date'})

        }