import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from mainapp.models import Category, Post, PersonalPost, LibText
from django.utils import timezone
from mainapp.views import get_combined_posts_for_category


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
    cat = Category.objects.create(name="Test Cat", slug="test-cat")
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
    cat = Category.objects.create(name="Test Cat", slug="test-cat")
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
    cat = Category.objects.create(name="Test Cat", slug="test-cat")
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


@pytest.mark.django_db
def test_get_combined_posts_for_category_returns_sorted_posts():
    user = User.objects.create_user(username="testuser", password="pass")
    cat = Category.objects.create(name="Test Category", slug="test-category")

    post_old = Post.objects.create(
        title="Old User Post",
        content="Old content",
        published_date=timezone.now() - timezone.timedelta(days=5),
        category=cat,
        user=user,
    )
    post_new = Post.objects.create(
        title="New User Post",
        content="New content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )
    libtext = LibText.objects.create(
        title="Admin Post",
        content="Admin content",
        to_category=cat,
    )

    combined = get_combined_posts_for_category(cat)
    titles = [p.title for p in combined]

    assert "Old User Post" in titles
    assert "New User Post" in titles
    assert "Admin Post" in titles

    assert combined[0].title == "New User Post"


@pytest.mark.django_db
def test_category_list_view_authenticated(client):
    user = User.objects.create_user(username="testuser", password="pass")
    cat = Category.objects.create(name="Test Category", slug="test-category")

    Post.objects.create(
        title="User Post",
        content="User content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )
    LibText.objects.create(
        title="Admin Post",
        content="Admin content",
        to_category=cat,
    )

    client.login(username="testuser", password="pass")
    url = reverse("mainapp:library_posts_by_category", kwargs={"slug": cat.slug})
    response = client.get(url)

    assert response.status_code == 200
    context = response.context
    assert context["category"] == cat
    assert cat in context["categories"]

    posts = context["posts"]
    titles = [p.title for p in posts]
    assert "User Post" in titles
    assert "Admin Post" in titles


@pytest.mark.django_db
def test_category_list_view_unauthenticated(client):
    cat = Category.objects.create(name="Test Category", slug="test-category")
    url = reverse("mainapp:library_posts_by_category", kwargs={"slug": cat.slug})
    response = client.get(url)
    assert response.status_code == 302
