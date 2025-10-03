import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock

from mainapp.models import PersonalPost, Survey, Answers, UserAnswer


@pytest.mark.django_db
def test_index_view(client):
    url = reverse("mainapp:index")
    response = client.get(url)
    assert response.status_code == 200
    assert "mainapp/index.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_survey_view_get(client):
    user = User.objects.create_user(username="user2", password="pass")
    client.login(username="user2", password="pass")

    url = reverse("mainapp:checkme")
    response = client.get(url)
    assert response.status_code == 200
    assert "mainapp/checkme.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_survey_view_post_all_answered(client):
    user = User.objects.create_user(username="user3", password="pass")
    client.login(username="user3", password="pass")

    survey = Survey.objects.create(question="Q1")
    answer = Answers.objects.create(survey=survey, choice_text="A1", marker="good")

    url = reverse("mainapp:checkme")
    data = {f"survey_{survey.id}": answer.id}
    with patch("mainapp.views.get_answer_by_id", return_value=answer):
        with patch("mainapp.views.save_user_answers_bulk") as mock_save:
            response = client.post(url, data)
            assert response.status_code == 200
            mock_save.assert_called_once()


@pytest.mark.django_db
def test_survey_history_view(client):
    user = User.objects.create_user(username="user4", password="pass")
    client.login(username="user4", password="pass")

    survey = Survey.objects.create(question="Q2")
    answer = Answers.objects.create(survey=survey, choice_text="A2", marker="neutral")
    ua = UserAnswer.objects.create(user=user, survey=survey, answer_choice=answer, date=timezone.localdate())

    url = reverse("mainapp:survey_history")
    response = client.get(url)
    assert response.status_code == 200
    assert ua in response.context["history"][ua.date]


@pytest.mark.django_db
def test_monthly_analytics_view(client):
    user = User.objects.create_user(username="user5", password="pass")
    client.login(username="user5", password="pass")

    url = reverse("mainapp:monthly_analytics")
    with patch("mainapp.views.get_monthly_analytics", return_value="message"):
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["message"] == "message"


@pytest.mark.django_db
def test_post_history_view(client):
    user = User.objects.create_user(username="user8", password="pass")
    client.login(username="user8", password="pass")

    with patch("mainapp.views.get_personal_posts_by_user", return_value=[]):
        with patch("mainapp.views.get_user_spotify_token", return_value=("token", True)):
            url = reverse("mainapp:post_history")
            response = client.get(url)
            assert response.status_code == 200
            assert "posts_with_track" in response.context
