from itertools import chain

from django.contrib import messages
from django.shortcuts import  redirect, get_object_or_404
from django.db.models import Q
from .forms import PersonalPostForm, PostForm
from django.contrib.auth.decorators import login_required
from .models import Category,  Survey, Answers, LibText, Post
from django.http import HttpResponse
from gallery.models import GalleryDay
import calendar
from datetime import date, timedelta
from django.utils import timezone
from django.shortcuts import render
from .models import PersonalPost, UserAnswer
from dateutil import parser
from django.utils.translation import gettext as _



# Користувача персональний
@login_required()
def post(request, id=None):
    post = get_object_or_404(Post, title=id)
    context = {"post": post, }
    return  render(request, 'mainapp/post.html', context=context)


def index(request):
    return render(request, 'mainapp/index.html')


@login_required()
def success(request):
    return HttpResponse('successfully uploaded')



@login_required
def survey_view(request):
    surveys = Survey.objects.prefetch_related('answers').all()
    today = timezone.now().date()
    already_answered = UserAnswer.objects.filter(user=request.user, date=today).exists()# 🔒 Перевірка: чи вже відповідав сьогодні
    if already_answered:
        return render(request, 'mainapp/already_answered.html')  # Сторінка з повідомленням

    if request.method == 'POST':
        all_answered = True
        answers_to_save = []
        for survey in surveys:
            selected_answer = request.POST.get(f"survey_{survey.id}")
            if selected_answer:
                answer_choice = Answers.objects.get(id=selected_answer)
                answers_to_save.append(UserAnswer(
                    user=request.user,
                    survey=survey,
                    answer_choice=answer_choice,
                    date=today))
            else:
                all_answered = False
        if all_answered:
            UserAnswer.objects.bulk_create(answers_to_save)# Зберігаємо всі відповіді разом
            return render(request, 'mainapp/survey_thanks.html')
        else:
            error = _("Будь ласка, дайте відповідь на всі питання.")
            return render(request, 'mainapp/checkme.html', {
                'surveys': surveys,
                'error': error})
    return render(request, 'mainapp/checkme.html', {'surveys': surveys})


@login_required
def survey_history(request):
    user_answers = (
        UserAnswer.objects.filter(user=request.user).select_related('survey', 'answer_choice').order_by('-date', 'survey__id'))
    history = {}
    for answer in user_answers:
        history.setdefault(answer.date, []).append(answer)
    return render(request, 'mainapp/survey_history.html', {'history': history})


def get_monthly_analytics(user):
    now = timezone.now()
    start_of_month = now.replace(day=1)
    end_of_month = now

    answers = UserAnswer.objects.filter(
        user=user,
        answered_at__date__gte=start_of_month,
        answered_at__date__lte=end_of_month
    ).select_related('answer_choice') # Витягни всі записи, де дата відповіді більша або дорівнює першому числу місяця І менша або дорівнює сьогоднішній даті

    counts = {'good': 0, 'neutral': 0, 'bad': 0}

    for answer in answers:
        marker = answer.answer_choice.marker # кожної відповіді користувача ми отримуємо маркер
        if marker in counts: # перевіряємо, чи цей маркер є в словнику
            counts[marker] += 1

    max_value = max(counts.values())

    if list(counts.values()).count(max_value) > 1:
        return _("немає вектору в конкретну сторону, в цьому місяці ти ні там ні там")
    elif counts['good'] == max_value:
        return _("у цьому місяці динаміка супер крута")
    elif counts['neutral'] == max_value:
        return _("цього місяця тримаємось середнього")
    else:
        return _("в цьому місяці усе погано")


def monthly_analytics_view(request):
    message = get_monthly_analytics(request.user)
    return render(request, 'mainapp/monthly_analytics.html', {'message': message})


def get_daily_data(user, selected_date):
    # Дати, коли щось є в будь-якій з моделей
    data_dates = set(
        GalleryDay.objects.filter(user=user).values_list("date", flat=True)
    ) | set(
        PersonalPost.objects.filter(user=user).values_list("date", flat=True)
    ) | set(
        UserAnswer.objects.filter(user=user).values_list("date", flat=True)
    )

    # Галерея — фото і відео через GalleryDay
    gallery_day = GalleryDay.objects.filter(user=user, date=selected_date).first()
    if gallery_day:
        gallery_items = gallery_day.photos.all()  # пов’язано через related_name='photos'
        video_items = gallery_day.videos.all()    # пов’язано через related_name='videos'
    else:
        gallery_items = []
        video_items = []

    # Пости й опитування
    personal_post = PersonalPost.objects.filter(user=user, date=selected_date).first()
    survey_answers = UserAnswer.objects.filter(user=user, date=selected_date).select_related('survey', 'answer_choice')

    return {
        "data_dates": data_dates,
        "gallery_items": gallery_items,
        "video_items": video_items,
        "personal_post": personal_post,
        "survey_answers": survey_answers,
    }



@login_required
def calendar_combined_view(request):
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    selected_date = request.GET.get('date')
    if 'month' in request.GET:# Перемикання місяця назад вперед
        month = int(request.GET.get('month'))
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
    start_day = date(year, month, 1)
    start_weekday = start_day.weekday()
    start_blank_days = start_weekday
    if selected_date:# Формування тижнів
        try:
            selected_date = parser.parse(selected_date).date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today
    start_day_of_week, days_in_month = calendar.monthrange(year, month)
    calendar_days = [start_day + timedelta(days=i) for i in range(days_in_month)]
    all_days = [None] * start_blank_days + calendar_days
    weeks = [all_days[i:i + 7] for i in range(0, len(all_days), 7)]
    user = request.user
    daily_data = get_daily_data(user, selected_date)
    context = {
        "year": year,
        "month": month,
        "calendar_days": calendar_days,
        "today": today,
        "selected_date": selected_date,
        "weekdays": [_("Пн"), _("Вт"), _("Ср"), _("Чт"), _("Пт"), _("Сб"), _("Нд")],
        "start_blank_days": range(start_blank_days),
        "calendar_weeks": weeks,
        **daily_data,
    }
    return render(request, "mainapp/calendar.html", context)




@login_required()
def search(request):
    query = request.GET.get('query', '')
    post_blog_list = Post.objects.filter(Q(content__icontains=query) | Q(title__icontains=query)).order_by("-published_date")
    my_posts_list = LibText.objects.filter(content__icontains=query )
    categories = Category.objects.all()

    context = {'post_blog_list': post_blog_list,
               'my_posts_list': my_posts_list,
               'query': query,
               'categories': categories,}
    return render(request, 'mainapp/library.html', context=context)


@login_required()
def home(request):
    return render(request, 'mainapp/home.html')


@login_required()
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.published_date = timezone.now()
            post.user = request.user
            post.save()
            form.save_m2m()  # ← для ManyToMany поля "teg"(в тг
            return redirect('mainapp:library_history')
    form = PostForm()
    context = {"form": form}
    return render(request, 'mainapp/create.html', context=context)


@login_required()
def category_list_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category)
    context = {'categories': category, 'posts':posts}
    return render(request, 'mainapp/library.html', context=context)


@login_required()
def posts_by_category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = category.posts.all()
    return render(request, 'mainapp/library.html', {'category': category,'posts': posts})


@login_required()
def library_view(request, slug=None):
    categories = Category.objects.all()
    posts = None
    selected_category = None
    if slug:
        selected_category = get_object_or_404(Category, slug=slug)
        user_posts = selected_category.posts.all()
        admin_posts = selected_category.libtexts.all()

        posts = sorted(
            chain(user_posts, admin_posts),
            key=lambda x: getattr(x, 'published_date', timezone.now()),
            reverse=True
        )
    return render(request, 'mainapp/library.html', {
        'categories': categories,
        'selected_category': selected_category,
        'posts': posts,
    })



@login_required
def daily_post_view(request):
    today = timezone.now().date()
    post = PersonalPost.objects.filter(user=request.user, date=today).first()

    if request.method == 'POST':
        form = PersonalPostForm(request.POST, instance=post) if post else PersonalPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            if not post.user_id:
                post.user = request.user
            post.save()
            messages.success(request, _("Запис успішно збережено!"))
            return redirect('mainapp:post_history')
    else:
        form = PersonalPostForm(instance=post) if post else PersonalPostForm()

    return render(request, 'mainapp/personal_post.html', {'form': form})


@login_required
def post_history_view(request):
    posts = PersonalPost.objects.filter(user=request.user).order_by('-date')
    return render(request, 'mainapp/personal_post_history.html', {'posts': posts})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings   # ← Ось тут ти підключаєш те, що ти зберегла в settings.py
import json
import requests

# Відображає сторінку з чатом
def chat_page(request):
    return render(request, 'mainapp/home.html')

# Обробляє запит від форми (чат)
@csrf_exempt
def ai_assistant(request):

    if request.method == 'POST':
        try:

            data = json.loads(request.body)
            message = data.get('message')
            print("🔵 Отримано повідомлення:", message)
            print("📡 Звертаємось до Ollama...")

            response = requests.post(
                f"{settings.OLLAMA_API_URL}/api/generate",
                json={
                    "model": "mistral",
                    "prompt": message,
                }
            )
            result = response.json()
            print("🟢 Відповідь від Ollama:", result)
            return JsonResponse({'reply': result.get('response', 'Вибач, не можу відповісти.')})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def library_users_history(request):
    posts = Post.objects.filter(user=request.user).order_by('-published_date')
    return render(request, 'mainapp/lib_user_post_history.html', {'posts': posts})