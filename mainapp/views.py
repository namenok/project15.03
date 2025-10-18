from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

from .forms import PersonalPostForm
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

from spotify_utils import (get_spotify_token, get_user_spotify_token, get_token_from_code,
    search_spotify_track, is_premium_user)
from .models import Track, SpotifyToken 
from datetime import timedelta
import urllib.parse

import json
from mainapp.services.personal_post_service import (
    get_today_personal_post,
    get_personal_posts_by_user,
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
    user = request.user

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
    user_token, premium_user = get_user_spotify_token(user)
    track = Track.objects.filter(user=user, date=selected_date).first()

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
        "track": track,
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



@login_required()
def home(request):
    return render(request, "mainapp/home.html")



@login_required
def daily_post_view(request):
    today = timezone.localdate()
    post = get_today_personal_post(request.user)
    saved_track = Track.objects.filter(user=request.user, date=today).first() 

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

    user_token, premium_user = get_user_spotify_token(request.user)
    print("USER:", request.user)
    print("USER TOKEN:", user_token)
    print("PREMIUM USER:", premium_user)

    return render(
        request,
        "mainapp/personal_post.html",
        {
            "form": form, 
            "saved_track": saved_track, 
            "user_token": user_token,
            "premium_user": premium_user,
        }
    )


@login_required
def post_history_view(request):
    posts = get_personal_posts_by_user(request.user)

    user_token, premium_user = get_user_spotify_token(request.user)

    posts_with_track = []
    for post in posts:
        track = Track.objects.filter(user=request.user, date=post.date).first()
        posts_with_track.append({
            "post": post,
            "track": track
        })

    return render(request, "mainapp/personal_post_history.html", {
        "posts_with_track": posts_with_track,
        "user_token": user_token,
        "premium_user": premium_user})


@login_required
def chat_page(request):
    return render(request, "mainapp/home.html")




@login_required
def spotify_search(request):
    today = timezone.localdate()
    post = get_today_personal_post(request.user)
    
    if request.method == "POST" and 'text' in request.POST: 
        form = PersonalPostForm(request.POST, instance=post)
        if form.is_valid():
            personal_post_instance = form.save(commit=False)
            personal_post_instance.user = request.user
            personal_post_instance.date = today
            personal_post_instance.save()
            messages.success(request, _("Запис успішно збережено"))
            return redirect('mainapp:spotify_search')
    else:
        form = PersonalPostForm(instance=post)

   
    saved_track = Track.objects.filter(user=request.user, date=today).first()
    query = request.GET.get('q')
    results = search_spotify_track(query) if query else []

    
    if request.method == 'POST' and 'track_id' in request.POST:
        track_id = request.POST['track_id']
        Track.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={'spotify_track_id': track_id}
        )
        return redirect('mainapp:spotify_search')

    user_token, premium_user = get_user_spotify_token(request.user)

    return render(request, 'mainapp/personal_post.html', {
        'form': form,
        'saved_track': saved_track,
        'results': results,
        'query': query,
        'user_token': user_token,
        'premium_user': premium_user,
    })



def spotify_callback(request):
    code = request.GET.get("code")
    if not code:
        return redirect("mainapp:post_history")  

    token_data = get_token_from_code(code)
    if not token_data:
        return redirect("mainapp:post_history")

    user_id = request.session.pop('spotify_user_id', None)
    if not user_id:
        return redirect("mainapp:post_history")

    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("mainapp:post_history")

    SpotifyToken.objects.update_or_create(
        user=request.user,
        defaults={
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "created_at": timezone.now(),
        }
    )

    return redirect("mainapp:post_history")


def spotify_login(request):
    request.session['spotify_user_id'] = request.user.id

    scope = "streaming user-read-email user-read-private user-modify-playback-state"
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "scope": scope,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "show_dialog": "true"
    })
    return redirect(auth_url)
