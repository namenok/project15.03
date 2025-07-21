import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from mainapp.models import Category, Post, PersonalPost
from django.utils import timezone


@pytest.mark.django_db
def test_index_view(client):
    url = reverse("mainapp:index")
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "ласкаво просимо" in content or "MindSpace" in content


@pytest.mark.django_db
def test_post_view_authenticated(client):
    user = User.objects.create_user(username="testuser", password="pass")
    cat = Category.objects.create(name="Test Cat")
    post = Post.objects.create(
        title="Test Post",
        content="Some content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )
    client.login(username="testuser", password="pass")
    url = reverse("mainapp:post", args=[post.title])
    response = client.get(url)
    assert response.status_code == 200
    assert b"Test Post" in response.content


@pytest.mark.django_db
def test_post_view_unauthenticated(client):
    cat = Category.objects.create(name="Test Cat")
    user = User.objects.create_user(username="testuser", password="pass")
    post = Post.objects.create(
        title="Test Post",
        content="Some content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )
    url = reverse("mainapp:post", args=[post.title])
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_post_view(client):
    User.objects.create_user(username="testuser", password="pass")
    cat = Category.objects.create(name="Test Cat")
    client.login(username="testuser", password="pass")
    url = reverse("mainapp:create")
    data = {
        "title": "New Post",
        "content": "Some content",
        "category": cat.id,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Post.objects.filter(title="New Post").exists()


@pytest.mark.django_db
def test_daily_post_view(client):
    User.objects.create_user(username="testuser", password="pass")
    client.login(username="testuser", password="pass")
    url = reverse("mainapp:daily_post")
    data = {
        "title": "Diary",
        "content": "My day",
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert PersonalPost.objects.filter(title="Diary").exists()


@pytest.mark.django_db
def test_home_view_authenticated(client):
    User.objects.create_user(username="testuser", password="pass")
    client.login(username="testuser", password="pass")
    url = reverse("mainapp:home")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_view_unauthenticated(client):
    url = reverse("mainapp:home")
    response = client.get(url)
    assert response.status_code == 302
