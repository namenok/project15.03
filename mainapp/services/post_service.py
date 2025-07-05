from mainapp.models import Post
from django.shortcuts import get_object_or_404


def get_post_by_title(title):
    return get_object_or_404(Post, title=title)


def get_posts_by_category(category):
    return Post.objects.filter(category=category)


def get_posts_by_user(user):
    return Post.objects.filter(user=user).order_by("-published_date")


def search_posts(query):
    from django.db.models import Q

    return Post.objects.filter(
        Q(content__icontains=query) | Q(title__icontains=query)
    ).order_by("-published_date")
