import pytest
from mainapp.models import Survey, UserAnswer, Answers, User
from mainapp.services.survey_service import (
    get_all_surveys,
    has_user_answered_today,
    get_user_answers,
    get_answer_by_id,
    save_user_answers_bulk,
)
from django.utils import timezone


@pytest.mark.django_db
def test_get_all_surveys():
    s1 = Survey.objects.create(question="Q1?")
    s2 = Survey.objects.create(question="Q2?")
    surveys = list(get_all_surveys())
    assert s1 in surveys and s2 in surveys
    assert len(surveys) == 2


@pytest.mark.django_db
def test_has_user_answered_today():
    user = User.objects.create_user(username="testuser", password="pass")
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="good", survey=survey, choice_text="Good")
    assert not has_user_answered_today(user)
    UserAnswer.objects.create(
        user=user, survey=survey, answer_choice=ans, date=timezone.now().date()
    )
    assert has_user_answered_today(user)


@pytest.mark.django_db
def test_get_user_answers():
    user = User.objects.create_user(username="testuser2", password="pass")
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="neutral", survey=survey, choice_text="Ok")
    ua = UserAnswer.objects.create(
        user=user, survey=survey, answer_choice=ans, date=timezone.now().date()
    )
    answers = list(get_user_answers(user))
    assert ua in answers
    assert answers[0].survey == survey


@pytest.mark.django_db
def test_get_answer_by_id_found():
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="bad", survey=survey, choice_text="Bad")
    result = get_answer_by_id(ans.id)
    assert result == ans
    assert result.choice_text == "Bad"


@pytest.mark.django_db
def test_get_answer_by_id_not_found():
    with pytest.raises(Exception):
        get_answer_by_id(9999)


@pytest.mark.django_db
def test_save_user_answers_bulk():
    user = User.objects.create_user(username="testuser3", password="pass")
    survey = Survey.objects.create(question="Q?")
    ans = Answers.objects.create(marker="good", survey=survey, choice_text="Good")
    ua1 = UserAnswer(
        user=user, survey=survey, answer_choice=ans, date=timezone.now().date()
    )
    ua2 = UserAnswer(
        user=user,
        survey=survey,
        answer_choice=ans,
        date=timezone.now().date() - timezone.timedelta(days=1),
    )
    save_user_answers_bulk([ua1, ua2])
    assert UserAnswer.objects.count() == 2
