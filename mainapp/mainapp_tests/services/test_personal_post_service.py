import pytest
from mainapp.models import PersonalPost, User
from mainapp.services.personal_post_service import (
    get_today_personal_post,
    get_personal_post_by_id,
    get_personal_posts_by_user,
)
from datetime import date
from django.utils import timezone


@pytest.mark.django_db
def test_get_today_personal_post():
    user = User.objects.create_user(username="testuser", password="pass")
    today = timezone.localdate()
    post = PersonalPost.objects.create(
        title="Diary", content="My day", user=user, date=today
    )
    result = get_today_personal_post(user)
    assert result == post
    assert result.date == today


@pytest.mark.django_db
def test_get_today_personal_post_none():
    user = User.objects.create_user(username="testuser2", password="pass")
    assert get_today_personal_post(user) is None


@pytest.mark.django_db
def test_get_personal_post_by_id_found():
    user = User.objects.create_user(username="testuser3", password="pass")
    post = PersonalPost.objects.create(
        title="Diary2", content="Day2", user=user, date=date.today()
    )
    result = get_personal_post_by_id(post.id)
    assert result == post


@pytest.mark.django_db
def test_get_personal_post_by_id_not_found():
    with pytest.raises(Exception):
        get_personal_post_by_id(9999)


@pytest.mark.django_db
def test_get_personal_posts_by_user():
    user = User.objects.create_user(username="testuser4", password="pass")
    post1 = PersonalPost.objects.create(
        title="A", content="A", user=user, date=date.today()
    )
    post2 = PersonalPost.objects.create(
        title="B", content="B", user=user, date=date.today()
    )
    posts = list(get_personal_posts_by_user(user))
    assert post1 in posts and post2 in posts
    assert len(posts) == 2
