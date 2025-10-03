import pytest
from django.contrib.auth.models import User
from django.http import Http404
from django.utils import timezone
from datetime import timedelta

from mainapp.models import Survey, Answers, UserAnswer
from mainapp.services.survey_service import (
    get_all_surveys,
    has_user_answered_today,
    get_user_answers,
    get_answer_by_id,
    save_user_answers_bulk,
)


@pytest.mark.django_db
def test_get_all_surveys_returns_surveys_with_answers():
    survey = Survey.objects.create(question="How are you?")
    answer = Answers.objects.create(
        marker="good", survey=survey, choice_text="Great!"
    )
    surveys = list(get_all_surveys())
    assert surveys[0] == survey
    assert list(surveys[0].answers.all()) == [answer]


@pytest.mark.django_db
def test_has_user_answered_today_true_and_false():
    user = User.objects.create_user(username="testuser")
    survey = Survey.objects.create(question="How are you?")
    answer = Answers.objects.create(marker="good", survey=survey, choice_text="Fine")
    today = timezone.localdate()

    UserAnswer.objects.create(user=user, survey=survey, answer_choice=answer, date=today)
    assert has_user_answered_today(user) is True

    another_user = User.objects.create_user(username="another")
    assert has_user_answered_today(another_user) is False


@pytest.mark.django_db
def test_get_user_answers_ordered():
    user = User.objects.create_user(username="testuser")
    survey1 = Survey.objects.create(question="Q1")
    survey2 = Survey.objects.create(question="Q2")
    a1 = Answers.objects.create(marker="neutral", survey=survey1, choice_text="Ok")
    a2 = Answers.objects.create(marker="bad", survey=survey2, choice_text="Bad")

    today = timezone.localdate()
    yesterday = today - timezone.timedelta(days=1)

    ua1 = UserAnswer.objects.create(user=user, survey=survey1, answer_choice=a1, date=yesterday)
    ua2 = UserAnswer.objects.create(user=user, survey=survey2, answer_choice=a2, date=today)

    results = list(get_user_answers(user))
    assert results == [ua2, ua1]


@pytest.mark.django_db
def test_get_answer_by_id_success_and_404():
    survey = Survey.objects.create(question="Q?")
    answer = Answers.objects.create(marker="good", survey=survey, choice_text="Great")
    result = get_answer_by_id(answer.id)
    assert result == answer

    with pytest.raises(Http404):
        get_answer_by_id(9999)


@pytest.mark.django_db
def test_save_user_answers_bulk_creates_multiple():
    user = User.objects.create_user(username="testuser")
    survey = Survey.objects.create(question="Bulk?")
    a1 = Answers.objects.create(marker="good", survey=survey, choice_text="Yes")
    a2 = Answers.objects.create(marker="bad", survey=survey, choice_text="No")

    today = timezone.localdate()
    ua1 = UserAnswer(user=user, survey=survey, answer_choice=a1, date=today)
    ua2 = UserAnswer(user=user, survey=survey, answer_choice=a2, date=today + timedelta(days=1))

    save_user_answers_bulk([ua1, ua2])

    results = UserAnswer.objects.filter(user=user)
    assert results.count() == 2
    assert {ua.answer_choice for ua in results} == {a1, a2}
