import pytest
from django.contrib.auth.models import User
from django.http import Http404
from django.utils import timezone

from mainapp.models import Survey, Answers, UserAnswer
from mainapp.services.user_answer_service import (
    get_user_answers_for_date,
    get_user_answers_in_month,
    get_user_answer_by_id,
    get_all_user_answers,
)


@pytest.mark.django_db
def test_get_user_answers_for_date_returns_only_today():
    user = User.objects.create_user(username="testuser")
    survey = Survey.objects.create(question="Q1")
    answer = Answers.objects.create(marker="good", survey=survey, choice_text="Ok")
    today = timezone.localdate()
    yesterday = today - timezone.timedelta(days=1)

    ua_today = UserAnswer.objects.create(user=user, survey=survey, answer_choice=answer, date=today)
    UserAnswer.objects.create(user=user, survey=survey, answer_choice=answer, date=yesterday)

    results = list(get_user_answers_for_date(user, today))
    assert results == [ua_today]


@pytest.mark.django_db
def test_get_user_answers_in_month_range():
    user = User.objects.create_user(username="testuser")
    survey = Survey.objects.create(question="Q2")
    answer = Answers.objects.create(marker="neutral", survey=survey, choice_text="meh")

    today = timezone.localdate()
    start = today - timezone.timedelta(days=5)
    end = today + timezone.timedelta(days=5)

    ua = UserAnswer.objects.create(user=user, survey=survey, answer_choice=answer, date=today)
    results = list(get_user_answers_in_month(user, start, end))
    assert results == [ua]


@pytest.mark.django_db
def test_get_user_answer_by_id_success_and_404():
    user = User.objects.create_user(username="testuser")
    survey = Survey.objects.create(question="Q3")
    answer = Answers.objects.create(marker="bad", survey=survey, choice_text="No")

    ua = UserAnswer.objects.create(user=user, survey=survey, answer_choice=answer, date=timezone.localdate())
    result = get_user_answer_by_id(ua.id)
    assert result == ua

    with pytest.raises(Http404):
        get_user_answer_by_id(9999)


@pytest.mark.django_db
def test_get_all_user_answers_ordering():
    user = User.objects.create_user(username="testuser")
    survey1 = Survey.objects.create(question="Q1")
    survey2 = Survey.objects.create(question="Q2")
    a1 = Answers.objects.create(marker="good", survey=survey1, choice_text="Yes")
    a2 = Answers.objects.create(marker="bad", survey=survey2, choice_text="No")

    today = timezone.localdate()
    yesterday = today - timezone.timedelta(days=1)

    ua1 = UserAnswer.objects.create(user=user, survey=survey1, answer_choice=a1, date=yesterday)
    ua2 = UserAnswer.objects.create(user=user, survey=survey2, answer_choice=a2, date=today)

    results = list(get_all_user_answers(user))
    assert results == [ua2, ua1]
