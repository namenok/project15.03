import pytest
from mainapp.models import Category
from mainapp.services.category_service import get_category_by_slug, get_all_categories


@pytest.mark.django_db
def test_get_category_by_slug_found():
    cat = Category.objects.create(name="TestCat", slug="testcat")
    result = get_category_by_slug("testcat")
    assert result == cat  # nosec
    assert result.slug == "testcat"  # nosec


@pytest.mark.django_db
def test_get_category_by_slug_not_found():
    with pytest.raises(Exception):
        get_category_by_slug("not-exist")


@pytest.mark.django_db
def test_get_all_categories():
    cat1 = Category.objects.create(name="Cat1", slug="cat1")
    cat2 = Category.objects.create(name="Cat2", slug="cat2")
    cats = get_all_categories()
    assert set(cats) == {cat1, cat2}  # nosec
    assert cats.count() == 2  # nosec
