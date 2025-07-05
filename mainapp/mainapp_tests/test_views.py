import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from mainapp.models import Category, Post, PersonalPost
from django.utils import timezone


@pytest.mark.django_db
def test_index_view(client):
    url = reverse("mainapp:index")
    response = client.get(url)  # nosec
    assert response.status_code == 200  # nosec
    content = response.content.decode("utf-8")  # nosec
    assert "ласкаво просимо" in content or "MindSpace" in content  # nosec


@pytest.mark.django_db
def test_post_view_authenticated(client):
    user = User.objects.create_user(username="testuser", password="pass")  # nosec
    cat = Category.objects.create(name="Test Cat")  # nosec
    post = Post.objects.create(
        title="Test Post",
        content="Some content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )  # nosec
    client.login(username="testuser", password="pass")  # nosec
    url = reverse("mainapp:post", args=[post.title])
    response = client.get(url)  # nosec
    assert response.status_code == 200  # nosec
    assert b"Test Post" in response.content  # nosec


@pytest.mark.django_db
def test_post_view_unauthenticated(client):
    cat = Category.objects.create(name="Test Cat")  # nosec
    user = User.objects.create_user(username="testuser", password="pass")  # nosec
    post = Post.objects.create(
        title="Test Post",
        content="Some content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )  # nosec
    url = reverse("mainapp:post", args=[post.title])
    response = client.get(url)  # nosec
    assert response.status_code == 302  # Redirect to login  # nosec


@pytest.mark.django_db
def test_create_post_view(client):
    User.objects.create_user(username="testuser", password="pass")  # nosec
    cat = Category.objects.create(name="Test Cat")  # nosec
    client.login(username="testuser", password="pass")  # nosec
    url = reverse("mainapp:create")
    data = {
        "title": "New Post",
        "content": "Some content",
        "category": cat.id,
    }  # nosec
    response = client.post(url, data)  # nosec
    assert response.status_code == 302  # Redirect after creation  # nosec
    assert Post.objects.filter(title="New Post").exists()  # nosec


@pytest.mark.django_db
def test_daily_post_view(client):
    User.objects.create_user(username="testuser", password="pass")  # nosec
    client.login(username="testuser", password="pass")  # nosec
    url = reverse("mainapp:daily_post")
    data = {
        "title": "Diary",
        "content": "My day",
    }  # nosec
    response = client.post(url, data)  # nosec
    assert response.status_code == 302  # Redirect after save  # nosec
    assert PersonalPost.objects.filter(title="Diary").exists()  # nosec


@pytest.mark.django_db
def test_home_view_authenticated(client):
    User.objects.create_user(username="testuser", password="pass")  # nosec
    client.login(username="testuser", password="pass")  # nosec
    url = reverse("mainapp:home")
    response = client.get(url)  # nosec
    assert response.status_code == 200  # nosec


@pytest.mark.django_db
def test_home_view_unauthenticated(client):
    url = reverse("mainapp:home")
    response = client.get(url)  # nosec
    assert response.status_code == 302  # Redirect to login  # nosec
