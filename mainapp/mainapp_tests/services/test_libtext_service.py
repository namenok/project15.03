import pytest
from mainapp.models import LibText, Category
from mainapp.services.libtext_service import (
    get_libtext_by_id,
    get_all_libtexts,
    get_libtexts_by_category,
)


@pytest.mark.django_db
def test_get_libtext_by_id_found():
    cat = Category.objects.create(name="TestCat", slug="testcat")
    lib = LibText.objects.create(
        title="LibTitle", content="LibContent", to_category=cat
    )
    result = get_libtext_by_id(lib.id)
    assert result == lib  # nosec
    assert result.title == "LibTitle"  # nosec


@pytest.mark.django_db
def test_get_libtext_by_id_not_found():
    with pytest.raises(Exception):
        get_libtext_by_id(9999)


@pytest.mark.django_db
def test_get_all_libtexts():
    cat = Category.objects.create(name="Cat1", slug="cat1")
    lib1 = LibText.objects.create(title="Lib1", content="C1", to_category=cat)
    lib2 = LibText.objects.create(title="Lib2", content="C2", to_category=cat)
    libs = get_all_libtexts()
    assert set(libs) == {lib1, lib2}  # nosec
    assert libs.count() == 2  # nosec


@pytest.mark.django_db
def test_get_libtexts_by_category():
    cat1 = Category.objects.create(name="Cat1", slug="cat1")
    cat2 = Category.objects.create(name="Cat2", slug="cat2")
    lib1 = LibText.objects.create(title="Lib1", content="C1", to_category=cat1)
    lib2 = LibText.objects.create(title="Lib2", content="C2", to_category=cat2)
    libs_cat1 = get_libtexts_by_category(cat1)
    libs_cat2 = get_libtexts_by_category(cat2)
    assert list(libs_cat1) == [lib1]  # nosec
    assert list(libs_cat2) == [lib2]  # nosec
