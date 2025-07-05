from mainapp.models import Survey, UserAnswer, Answers
from django.utils import timezone
from django.shortcuts import get_object_or_404


def get_all_surveys():
    return Survey.objects.prefetch_related("answers").all()


def has_user_answered_today(user):
    today = timezone.now().date()
    return UserAnswer.objects.filter(user=user, date=today).exists()


def get_user_answers(user):
    return (
        UserAnswer.objects.filter(user=user)
        .select_related("survey", "answer_choice")
        .order_by("-date", "survey__id")
    )


def get_answer_by_id(answer_id):
    return get_object_or_404(Answers, id=answer_id)


def save_user_answers_bulk(answers_to_save):
    UserAnswer.objects.bulk_create(answers_to_save)
