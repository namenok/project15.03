from django import forms

from .models import PersonalPost, Post


# class LibUserPostForm(forms.ModelForm):
#     class Meta:
#         model = LibUserPost
#         exclude = ('published_date', 'user', )
#         widgets = {
#             'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Напиши свій пост на сьогодні...'})
#         }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('published_date',  )




class PersonalPostForm(forms.ModelForm):
    class Meta:
        model = PersonalPost
        exclude = ('published_date', 'user', )
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Напиши свій пост на сьогодні...'})
        }