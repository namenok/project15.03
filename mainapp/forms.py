from django import forms

from .models import Entry, Foto, Post, PersonalPost


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text', ]
        labels = {'text': 'Entry text'}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}


class FotoForm(forms.ModelForm):
    class Meta:
        model = Foto
        fields = ['image']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ("published_date", )


class PersonalPostForm(forms.ModelForm):
    class Meta:
        model = PersonalPost
        exclude = ("published_date", 'user')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Напиши свій пост на сьогодні...'})
        }