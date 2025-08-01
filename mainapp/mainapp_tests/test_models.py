import pytest
from django.contrib.auth.models import User
from mainapp.models import (
    Category,
    Post,
    PersonalPost,
    LibText,
    Survey,
    Answers,
    UserAnswer,
)
from django.utils import timezone
from datetime import date


@pytest.mark.django_db
def test_category_str_and_slug():
    cat = Category.objects.create(name="Test Category")
    assert str(cat) == "Test Category"
    assert cat.slug.startswith("test-category")


@pytest.mark.django_db
def test_post_str_and_fields():
    user = User.objects.create_user(username="testuser", password="pass")
    cat = Category.objects.create(name="Test Cat")
    post = Post.objects.create(
        title="Test Post",
        content="Some content",
        published_date=timezone.now(),
        category=cat,
        user=user,
    )
    assert str(post) == "Test Post"
    assert post.category == cat
    assert post.user == user


@pytest.mark.django_db
def test_personal_post_str_and_unique():
    user = User.objects.create_user(username="testuser2", password="pass")
    post = PersonalPost.objects.create(
        title="Diary", content="My day", user=user, date=date.today()
    )
    assert str(post) == f"{user.username} - {date.today()}"
    with pytest.raises(Exception):
        PersonalPost.objects.create(
            title="Diary", content="My day", user=user, date=date.today()
        )


@pytest.mark.django_db
def test_libtext_str():
    cat = Category.objects.create(name="LibCat")
    lib = LibText.objects.create(
        title="LibTitle", content="LibContent", to_category=cat
    )
    assert str(lib) == "LibTitle"
    assert lib.to_category == cat


@pytest.mark.django_db
def test_survey_and_answers():
    survey = Survey.objects.create(question="How are you?")
    ans = Answers.objects.create(marker="good", survey=survey, choice_text="Good!")
    assert str(survey) == "How are you?"
    assert str(ans) == "Good!"
    assert ans.survey == survey


@pytest.mark.django_db
def test_user_answer_str_and_unique():
    user = User.objects.create_user(username="testuser3", password="pass")
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="neutral", survey=survey, choice_text="Ok")
    ua = UserAnswer.objects.create(
        user=user, survey=survey, answer_choice=ans, date=date.today()
    )
    assert survey.question in str(ua)
    with pytest.raises(Exception):
        UserAnswer.objects.create(
            user=user, survey=survey, answer_choice=ans, date=date.today()
        )
