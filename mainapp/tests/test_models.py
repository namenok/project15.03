import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from datetime import date, timedelta, datetime, timezone

from mainapp.models import (
    PersonalPost, Survey, Answers, UserAnswer
)


@pytest.mark.django_db
def test_personal_post_str():
    user = User.objects.create_user(username="testuser")
    post = PersonalPost.objects.create(
        title="Hello",
        content="Some text",
        user=user,
        date=date.today(),
    )
    assert str(post) == f"{user.username} - {post.date}"


@pytest.mark.django_db
def test_personal_post_unique_together():
    user = User.objects.create_user(username="testuser")
    PersonalPost.objects.create(
        title="Hello",
        content="Some text",
        user=user,
        date=date.today(),
    )
    with pytest.raises(IntegrityError):
        PersonalPost.objects.create(
            title="Another",
            content="Some text",  
            user=user,
            date=date.today(),
        )


@pytest.mark.django_db
def test_survey_and_answers():
    survey = Survey.objects.create(question="How are you?")
    answer = Answers.objects.create(
        marker="good", survey=survey, choice_text="Very good!"
    )
    assert str(survey) == "How are you?"
    assert str(answer) == "Very good!"
    assert answer.survey == survey
    assert survey.answers.count() == 1


@pytest.mark.django_db
def test_user_answer_str_and_unique():
    user = User.objects.create_user(username="testuser")
    survey = Survey.objects.create(question="How are you?")
    answer = Answers.objects.create(marker="neutral", survey=survey, choice_text="Ok")
    ua = UserAnswer.objects.create(
        user=user, survey=survey, answer_choice=answer, date=date.today()
    )

    assert str(ua) == f"відповідь {user.username} на {survey.question} {ua.date}"

    with pytest.raises(IntegrityError):
        UserAnswer.objects.create(
            user=user, survey=survey, answer_choice=answer, date=date.today()
        )



