from mainapp.models import Category
from django.shortcuts import get_object_or_404


def get_category_by_slug(slug):
    return get_object_or_404(Category, slug=slug)


def get_all_categories():
    return Category.objects.all()
