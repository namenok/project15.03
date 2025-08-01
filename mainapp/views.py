from django.contrib import messages
from django.shortcuts import redirect

from .forms import PersonalPostForm, PostForm
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from gallery.models import GalleryDay
import calendar
from datetime import date, timedelta
from datetime import datetime

from django.utils import timezone
from django.shortcuts import render
from .models import PersonalPost, UserAnswer
from dateutil import parser
from django.utils.translation import gettext as _, gettext

import aiohttp

import json
from mainapp.services.category_service import get_category_by_slug, get_all_categories
from mainapp.services.libtext_service import get_all_libtexts, get_libtexts_by_category
from mainapp.services.personal_post_service import (
    get_today_personal_post,
    get_personal_posts_by_user,
)
from mainapp.services.post_service import (
    get_post_by_title,
    get_posts_by_category,
    get_posts_by_user,
    search_posts,
)
from mainapp.services.survey_service import (
    get_all_surveys,
    has_user_answered_today,
    get_user_answers,
    get_answer_by_id,
    save_user_answers_bulk,
)
from mainapp.services.user_answer_service import (
    get_user_answers_for_date,
    get_user_answers_in_month,
)


# user`s personal post
@login_required()
def post(request, id=None):
    post = get_post_by_title(id)
    context = {"post": post}
    return render(request, "mainapp/post.html", context=context)


def index(request):
    return render(request, "mainapp/index.html")


@login_required()
def success(request):
    return HttpResponse("successfully uploaded")


@login_required
def survey_view(request):
    surveys = get_all_surveys()
    if has_user_answered_today(request.user):
        return render(request, "mainapp/already_answered.html")

    if request.method == "POST":
        all_answered = True
        answers_to_save = []
        for survey in surveys:
            selected_answer = request.POST.get(f"survey_{survey.id}")
            if selected_answer:
                answer_choice = get_answer_by_id(selected_answer)
                answers_to_save.append(
                    UserAnswer(
                        user=request.user,
                        survey=survey,
                        answer_choice=answer_choice,
                        date=timezone.now().date(),
                    )
                )
            else:
                all_answered = False
        if all_answered:
            save_user_answers_bulk(answers_to_save)
            return render(request, "mainapp/survey_thanks.html")
        else:
            error = _("будь ласка, дай відповідь на кожне питання")
            return render(
                request, "mainapp/checkme.html", {"surveys": surveys, "error": error}
            )
    return render(request, "mainapp/checkme.html", {"surveys": surveys})


@login_required
def survey_history(request):
    history = {}
    for answer in get_user_answers(request.user):
        history.setdefault(answer.date, []).append(answer)
    return render(request, "mainapp/survey_history.html", {"history": history})


def get_monthly_analytics(user):
    now = timezone.now()
    start_of_month = now.replace(day=1)
    end_of_month = now

    answers = get_user_answers_in_month(
        user,
        start_of_month,
        end_of_month,
    ).select_related("answer_choice")

    counts = {"good": 0, "neutral": 0, "bad": 0}

    for answer in answers:
        marker = answer.answer_choice.marker
        if marker in counts:
            counts[marker] += 1

    max_value = max(counts.values())

    if list(counts.values()).count(max_value) > 1:
        return _("немає вектору в конкретну сторону, цього місяця ми по середині")
    elif counts["good"] == max_value:
        return _("цього місяця динаміка позитивна")
    elif counts["neutral"] == max_value:
        return _("цього місяця тримаємось середнього")
    else:
        return _("цього місяця динаміка негативна")


def monthly_analytics_view(request):
    message = get_monthly_analytics(request.user)
    return render(request, "mainapp/monthly_analytics.html", {"message": message})


def get_daily_data(user, selected_date):
    gallery_day = GalleryDay.objects.filter(user=user, date=selected_date).first()
    if gallery_day:
        gallery_items = gallery_day.photos.all()
        video_items = gallery_day.videos.all()
    else:
        gallery_items = []
        video_items = []

    personal_post = PersonalPost.objects.filter(user=user, date=selected_date).first()
    survey_answers = get_user_answers_for_date(user, selected_date)

    return {
        "gallery_items": gallery_items,
        "video_items": video_items,
        "personal_post": personal_post,
        "survey_answers": survey_answers,
    }


@login_required
def calendar_combined_view(request):
    today = timezone.now().date()
    user = request.user  # Get the user early

    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    selected_date_str = request.GET.get("date")
    if selected_date_str:
        try:
            selected_date = parser.parse(selected_date_str).date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    start_day_of_month = date(year, month, 1)
    start_weekday = start_day_of_month.weekday()

    _, days_in_month = calendar.monthrange(year, month)

    calendar_days = [
        start_day_of_month + timedelta(days=i) for i in range(days_in_month)
    ]

    all_days = [None] * start_weekday + calendar_days

    weeks = [all_days[i : i + 7] for i in range(0, len(all_days), 7)]

    start_of_current_month = date(year, month, 1)
    end_of_current_month = date(year, month, calendar.monthrange(year, month)[1])

    all_dates_with_data_in_month = (
        set(
            GalleryDay.objects.filter(
                user=user,
                date__gte=start_of_current_month,
                date__lte=end_of_current_month,
            ).values_list("date", flat=True)
        )
        | set(
            PersonalPost.objects.filter(
                user=user,
                date__gte=start_of_current_month,
                date__lte=end_of_current_month,
            ).values_list("date", flat=True)
        )
        | set(
            UserAnswer.objects.filter(
                user=user,
                date__gte=start_of_current_month,
                date__lte=end_of_current_month,
            ).values_list("date", flat=True)
        )
    )

    daily_data = get_daily_data(user, selected_date)

    context = {
        "year": year,
        "month": month,
        "calendar_days": calendar_days,
        "today": today,
        "selected_date": selected_date,
        "weekdays": [
            gettext("Пн"),
            gettext("Вт"),
            gettext("Ср"),
            gettext("Чт"),
            gettext("Пт"),
            gettext("Сб"),
            gettext("Нд"),
        ],
        "start_blank_days": range(start_weekday),
        "calendar_weeks": weeks,
        "data_dates": all_dates_with_data_in_month,
        **daily_data,
    }
    return render(request, "mainapp/calendar.html", context)


def get_datetime_or_min(post):
    dt = getattr(post, "published_date", None) or getattr(post, "created_at", None)
    if dt is None:
        return timezone.make_aware(datetime.min.replace(year=1, month=1, day=1))
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


def get_combined_posts_for_category(category):
    user_posts = get_posts_by_category(category)
    admin_posts = get_libtexts_by_category(category)
    combined_posts = list(user_posts) + list(admin_posts)
    combined_posts.sort(key=get_datetime_or_min, reverse=True)
    return combined_posts


@login_required
def category_list_view(request, slug):
    category = get_category_by_slug(slug)
    combined_posts = get_combined_posts_for_category(category)
    categories = get_all_categories()
    context = {
        "category": category,
        "posts": combined_posts,
        "categories": categories,
    }
    return render(request, "mainapp/library.html", context)


@login_required()
def categories_overview(request):
    categories = get_all_categories()
    return render(request, "mainapp/library.html", {"categories": categories})


@login_required()
def library_users_history(request):
    posts = get_posts_by_user(request.user)
    return render(request, "mainapp/lib_user_post_history.html", {"posts": posts})


@login_required()
def search(request):
    query = request.GET.get("query", "")
    post_blog_list = search_posts(query)
    my_posts_list = get_all_libtexts().filter(content__icontains=query)
    categories = get_all_categories()
    context = {
        "post_blog_list": post_blog_list,
        "my_posts_list": my_posts_list,
        "query": query,
        "categories": categories,
    }
    return render(request, "mainapp/library.html", context=context)


@login_required()
def home(request):
    return render(request, "mainapp/home.html")


@login_required()
def create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.published_date = timezone.now()
            post.user = request.user
            post.save()
            form.save_m2m()
            return redirect("mainapp:library_history")
    form = PostForm()
    context = {"form": form}
    return render(request, "mainapp/create.html", context=context)


@login_required
def daily_post_view(request):
    today = timezone.localdate()
    post = get_today_personal_post(request.user)

    if request.method == "POST":
        form = PersonalPostForm(request.POST, instance=post)
        if form.is_valid():
            personal_post_instance = form.save(commit=False)
            if not personal_post_instance.user_id:
                personal_post_instance.user = request.user
            personal_post_instance.date = today
            try:
                personal_post_instance.save()
                messages.success(request, _("запис успішно збережено"))
                return redirect("mainapp:post_history")
            except Exception:
                messages.error(request, _("виникла помилка при збереженні"))
    else:
        form = PersonalPostForm(instance=post)
    return render(request, "mainapp/personal_post.html", {"form": form})


@login_required
def post_history_view(request):
    posts = get_personal_posts_by_user(request.user)
    return render(request, "mainapp/personal_post_history.html", {"posts": posts})


@login_required
def chat_page(request):
    return render(request, "mainapp/home.html")


async def query_ollama(ollama_url, payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(ollama_url, json=payload) as resp:
            full_response = ""
            async for line in resp.content:
                data = json.loads(line.decode())
                full_response += data.get("response", "")
                if data.get("done"):
                    break
            return full_response
