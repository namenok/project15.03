import pytest
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import Http404
from mainapp.models import PersonalPost
from mainapp.services.personal_post_service import (
    get_today_personal_post,
    get_personal_post_by_id,
    get_personal_posts_by_user,
)


@pytest.mark.django_db
def test_get_today_personal_post_returns_post():
    user = User.objects.create_user(username="testuser")
    today = timezone.localdate()
    post = PersonalPost.objects.create(
        title="Title",
        content="Content",
        user=user,
        date=today,
    )
    result = get_today_personal_post(user)
    assert result == post


@pytest.mark.django_db
def test_get_today_personal_post_returns_none_if_no_post():
    user = User.objects.create_user(username="testuser")
    result = get_today_personal_post(user)
    assert result is None


@pytest.mark.django_db
def test_get_personal_post_by_id_success():
    user = User.objects.create_user(username="testuser")
    post = PersonalPost.objects.create(
        title="Title",
        content="Content",
        user=user,
        date=timezone.localdate(),
    )
    result = get_personal_post_by_id(post.id)
    assert result == post


@pytest.mark.django_db
def test_get_personal_post_by_id_raises_404():
    with pytest.raises(Http404):
        get_personal_post_by_id(999)


@pytest.mark.django_db
def test_get_personal_posts_by_user_ordered():
    user = User.objects.create_user(username="testuser")
    post1 = PersonalPost.objects.create(
        title="Older",
        content="First",
        user=user,
        date=timezone.localdate() - timezone.timedelta(days=1),
    )
    post2 = PersonalPost.objects.create(
        title="Newer",
        content="Second",
        user=user,
        date=timezone.localdate(),
    )
    results = list(get_personal_posts_by_user(user))
    assert results == [post2, post1]
