import pytest
from mainapp.models import Post, Category, User
from mainapp.services.post_service import (
    get_post_by_title,
    get_posts_by_category,
    get_posts_by_user,
    search_posts,
)
from django.utils import timezone


@pytest.mark.django_db
def test_get_post_by_title_found():
    user = User.objects.create_user(username="testuser", password="pass")  # nosec
    cat = Category.objects.create(name="TestCat", slug="testcat")  # nosec
    post = Post.objects.create(
        title="Test Post",
        content="Some content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )
    result = get_post_by_title("Test Post")
    assert result == post  # nosec
    assert result.title == "Test Post"  # nosec


@pytest.mark.django_db
def test_get_post_by_title_not_found():
    with pytest.raises(Exception):
        get_post_by_title("not-exist")


@pytest.mark.django_db
def test_get_posts_by_category():
    user = User.objects.create_user(username="testuser2", password="pass")  # nosec
    cat1 = Category.objects.create(name="Cat1", slug="cat1")  # nosec
    cat2 = Category.objects.create(name="Cat2", slug="cat2")  # nosec
    post1 = Post.objects.create(
        title="A", content="A", published_date=timezone.now(), category=cat1, user=user
    )
    post2 = Post.objects.create(
        title="B", content="B", published_date=timezone.now(), category=cat2, user=user
    )
    posts_cat1 = list(get_posts_by_category(cat1))
    posts_cat2 = list(get_posts_by_category(cat2))
    assert post1 in posts_cat1  # nosec
    assert post2 in posts_cat2  # nosec
    assert post2 not in posts_cat1  # nosec


@pytest.mark.django_db
def test_get_posts_by_user():
    user1 = User.objects.create_user(username="user1", password="pass")  # nosec
    user2 = User.objects.create_user(username="user2", password="pass")  # nosec
    cat = Category.objects.create(name="Cat", slug="cat")
    post1 = Post.objects.create(
        title="A", content="A", published_date=timezone.now(), category=cat, user=user1
    )
    post2 = Post.objects.create(
        title="B", content="B", published_date=timezone.now(), category=cat, user=user2
    )
    posts_user1 = list(get_posts_by_user(user1))
    posts_user2 = list(get_posts_by_user(user2))
    assert post1 in posts_user1  # nosec
    assert post2 in posts_user2  # nosec
    assert post2 not in posts_user1  # nosec


@pytest.mark.django_db
def test_search_posts():
    user = User.objects.create_user(username="testuser3", password="pass")  # nosec
    cat = Category.objects.create(name="Cat", slug="cat")  # nosec
    post1 = Post.objects.create(
        title="FindMe",
        content="Some content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )
    post2 = Post.objects.create(
        title="Other",
        content="No match",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )
    results = list(search_posts("FindMe"))  # nosec
    assert post1 in results  # nosec
    assert post2 not in results  # nosec
