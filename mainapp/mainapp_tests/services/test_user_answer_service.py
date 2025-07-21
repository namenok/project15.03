import pytest
from mainapp.models import User, Survey, Answers, UserAnswer
from mainapp.services.user_answer_service import (
    get_user_answers_for_date,
    get_user_answers_in_month,
    get_user_answer_by_id,
    get_all_user_answers,
)
from datetime import date, timedelta


@pytest.mark.django_db
def test_get_user_answers_for_date():
    user = User.objects.create_user(username="testuser", password="pass")
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="good", survey=survey, choice_text="Good")
    ua = UserAnswer.objects.create(
        user=user, survey=survey, answer_choice=ans, date=date.today()
    )
    answers = list(get_user_answers_for_date(user, date.today()))
    assert ua in answers
    assert answers[0].survey == survey


@pytest.mark.django_db
def test_get_user_answers_in_month():
    user = User.objects.create_user(username="testuser2", password="pass")
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="neutral", survey=survey, choice_text="Ok")
    today = date.today()
    ua = UserAnswer.objects.create(
        user=user, survey=survey, answer_choice=ans, date=today
    )
    start = today.replace(day=1)
    end = today
    answers = list(get_user_answers_in_month(user, start, end))
    assert ua in answers


@pytest.mark.django_db
def test_get_user_answer_by_id_found():
    user = User.objects.create_user(username="testuser3", password="pass")
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="bad", survey=survey, choice_text="Bad")
    ua = UserAnswer.objects.create(
        user=user, survey=survey, answer_choice=ans, date=date.today()
    )
    result = get_user_answer_by_id(ua.id)
    assert result == ua


@pytest.mark.django_db
def test_get_user_answer_by_id_not_found():
    with pytest.raises(Exception):
        get_user_answer_by_id(9999)


@pytest.mark.django_db
def test_get_all_user_answers():
    user = User.objects.create_user(username="testuser4", password="pass")
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="good", survey=survey, choice_text="Good")
    ua1 = UserAnswer.objects.create(
        user=user, survey=survey, answer_choice=ans, date=date.today()
    )
    ua2 = UserAnswer.objects.create(
        user=user,
        survey=survey,
        answer_choice=ans,
        date=date.today() - timedelta(days=1),
    )
    answers = list(get_all_user_answers(user))
    assert ua1 in answers and ua2 in answers
    assert len(answers) == 2
