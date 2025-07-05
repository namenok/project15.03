import pytest
from django.contrib.auth.models import User
from mainapp.models import Category, PersonalPost, Post
from mainapp.forms import PersonalPostForm, PostForm
from django.utils import timezone
from datetime import date


@pytest.mark.django_db
def test_post_form_valid():
    user = User.objects.create_user(username="testuser", password="pass")  # nosec
    cat = Category.objects.create(name="Test Cat")
    data = {
        "title": "Test Post",
        "content": "Some content",
        "category": cat.id,
    }
    form = PostForm(data)
    assert form.is_valid()  # nosec
    post = form.save(commit=False)  # nosec
    post.user = user
    post.published_date = timezone.now()
    post.save()
    assert Post.objects.filter(title="Test Post").exists()  # nosec


@pytest.mark.django_db
def test_post_form_missing_fields():
    form = PostForm({})  # nosec
    assert not form.is_valid()  # nosec
    assert "title" in form.errors  # nosec
    assert "content" in form.errors  # nosec
    assert "category" in form.errors  # nosec


@pytest.mark.django_db
def test_personal_post_form_valid():
    user = User.objects.create_user(username="testuser2", password="pass")  # nosec
    data = {
        "title": "Diary",
        "content": "My day",
    }
    form = PersonalPostForm(data)
    assert form.is_valid()  # nosec
    post = form.save(commit=False)
    post.user = user
    post.date = date.today()
    post.save()  # nosec
    assert PersonalPost.objects.filter(title="Diary").exists()  # nosec


@pytest.mark.django_db
def test_personal_post_form_missing_fields():
    form = PersonalPostForm({})
    assert not form.is_valid()  # nosec
    assert "title" in form.errors  # nosec
    assert "content" in form.errors  # nosec
