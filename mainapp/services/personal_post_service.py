from mainapp.models import PersonalPost
from django.shortcuts import get_object_or_404
from django.utils import timezone


def get_today_personal_post(user):
    today = timezone.localdate()
    return PersonalPost.objects.filter(user=user, date=today).first()


def get_personal_post_by_id(post_id):
    return get_object_or_404(PersonalPost, id=post_id)


def get_personal_posts_by_user(user):
    return PersonalPost.objects.filter(user=user).order_by("-date")
