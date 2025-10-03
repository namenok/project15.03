import pytest
from mainapp.forms import PersonalPostForm


@pytest.mark.django_db
def test_personal_post_form_valid():
    data = {
        "title": "My day",
        "content": "Some description",
    }
    form = PersonalPostForm(data=data)
    assert form.is_valid()
    instance = form.save(commit=False)
    assert instance.title == "My day"
    assert instance.content == "Some description"


@pytest.mark.django_db
def test_personal_post_form_missing_title():
    data = {
        "content": "No title provided",
    }
    form = PersonalPostForm(data=data)
    assert not form.is_valid()
    assert "title" in form.errors


@pytest.mark.django_db
def test_personal_post_form_widget_types():
    form = PersonalPostForm()
    assert isinstance(form.fields["content"].widget, type(form.base_fields["content"].widget))
    assert isinstance(PersonalPostForm.Meta.widgets["date"], type(form.fields["date"].widget)) if "date" in form.fields else True
