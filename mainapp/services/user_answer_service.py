from mainapp.models import UserAnswer
from django.shortcuts import get_object_or_404


def get_user_answers_for_date(user, date):
    return UserAnswer.objects.filter(user=user, date=date).select_related(
        "survey", "answer_choice"
    )


def get_user_answers_in_month(user, start_date, end_date):
    return UserAnswer.objects.filter(
        user=user, date__gte=start_date, date__lte=end_date
    )


def get_user_answer_by_id(answer_id):
    return get_object_or_404(UserAnswer, id=answer_id)


def get_all_user_answers(user):
    return (
        UserAnswer.objects.filter(user=user)
        .select_related("survey", "answer_choice")
        .order_by("-date", "survey__id")
    )
