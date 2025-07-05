from mainapp.models import LibText
from django.shortcuts import get_object_or_404


def get_libtext_by_id(libtext_id):
    return get_object_or_404(LibText, id=libtext_id)


def get_all_libtexts():
    return LibText.objects.all()


def get_libtexts_by_category(category):
    return LibText.objects.filter(to_category=category)
