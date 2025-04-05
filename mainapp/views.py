from dbm.ndbm import library
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .forms import EntryForm, FotoForm, PostForm, PersonalPostForm
from django.contrib.auth.decorators import login_required
from .models import Category, Post, LibText, Teg, Survey, UserAnswer, Answers, PersonalPost
from django.http import HttpResponse




@login_required()
def image_upload(request):
    if request.method == 'POST':
        form = FotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('mainapp:home')
    else:
        form = FotoForm()
    return render(request, 'mainapp/image_uploads.html', {'form': form})


@login_required()
def success(request):
    return HttpResponse('successfully uploaded')


def index(request):
    return render(request, 'mainapp/index.html')






@login_required
def survey_view(request):
    surveys = Survey.objects.prefetch_related('answers').all()
    today = timezone.now().date()

    if request.method == 'POST':
        for survey in surveys:
            # Перевіряємо, чи вибрано варіант відповіді для кожного опитування
            selected_answer = request.POST.get(f"survey_{survey.id}")
            if selected_answer:
                # Отримуємо вибраний варіант
                answer_choice = Answers.objects.get(id=selected_answer)

                # Створюємо або оновлюємо відповідь для поточної дати
                UserAnswer.objects.create(
                    user=request.user,
                    survey=survey,
                    answer_choice=answer_choice,
                    date=today  # Зберігаємо поточну дату
                )
                return render(request, 'mainapp/survey_thanks.html')
        # redirect('survey_thanks') # Перенаправляємо користувача на сторінку з підтвердженням
    return render(request, 'mainapp/checkme.html', {'surveys': surveys})





@login_required()
def post(request, id=None):
    post = get_object_or_404(Post, title=id)
    context = {"post": post, }
    # context.update(get_categories(request))
    return  render(request, 'mainapp/post.html', context=context)


@login_required()
def calendar(request):
    user_answers = UserAnswer.objects.filter(user=request.user)
    return render(request, 'mainapp/calendar.html', {'user_answers': user_answers})


@login_required()
def new_entry(request):
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.owner = request.user
            new_entry.save()
            return redirect('mainapp:home')
    context = {'form': form}
    return render(request,'mainapp/new_entry.html', context=context)


@login_required()
def search(request):
    query = request.GET.get('query')

    post_blog_list = Post.objects.filter(Q(content__icontains=query) | Q(title__icontains=query)).order_by("-published_date")
    my_posts_list = LibText.objects.filter(content__icontains=query)
    context = {'post_blog_list': post_blog_list,
               'my_posts_list': my_posts_list}
    return render(request, 'mainapp/library.html', context=context)


@login_required()
def home(request):
    return render(request, 'mainapp/home.html')


@login_required()
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.published_date = timezone.now()
            post.save()
            return library(request)
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
        posts = selected_category.posts.all()
    return render(request, 'mainapp/library.html', {
        'categories': categories,
        'selected_category': selected_category,
        'posts': posts,
    })


from django.urls import reverse
@login_required
def daily_post_view(request):
    today = timezone.now().date()
    post, created = PersonalPost.objects.get_or_create(user=request.user, date=today)

    if request.method == 'POST':
        form = PersonalPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('mainapp:post_history')  # Або залишити на цій же сторінці
    else:
            form = PersonalPostForm(instance=post)
    return render(request, 'mainapp/personal_post.html', {'form': form, 'created': created})


@login_required
def post_history_view(request):
    posts = PersonalPost.objects.filter(user=request.user).order_by('-date')
    return render(request, 'mainapp/personal_post_history.html', {'posts': posts})