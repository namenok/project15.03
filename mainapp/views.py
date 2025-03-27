from django.shortcuts import render

from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .forms import EntryForm, FotoForm, PostForm
from django.contrib.auth.decorators import login_required
from .models import Category, Post, LibText, Teg

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
# Create your views here.

@login_required()
def get_categories(request):
    all = Category.objects.all()
    count = all.count()
    return {
        "cat1":all[:count//2],
        "cat2":all[count//2:]
    }


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


@login_required()
def home(request):
    title = "це мій домашній кабінет тут записую думки та картикни"
    context = {
        "title":title,}
    return render(request, 'mainapp/home.html', context=context)


@login_required()
def checkme(request):
    return render(request, 'mainapp/checkme.html')


@login_required()
def library(request):
    post_blog_list = Post.objects.all().order_by("-published_date")
    my_posts_list = LibText.objects.all()
    tegs = Teg.objects.all()

    context = {"post_blog_list": post_blog_list,
               "my_posts_list": my_posts_list,
               "tegs": tegs,}
    context.update(get_categories(request))
    return render(request, 'mainapp/library.html', context=context)


@login_required()
def post(request, id=None):
    post = get_object_or_404(Post, pk=id)
    context = {"post": post, }
    context.update(get_categories(request))
    return  render(request, 'mainapp/post.html', context=context)


@login_required()
def calendar(request):
    return render(request, 'mainapp/calendar.html')


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
    return render(
        request,
        'mainapp/new_entry.html',
        context=context)



@login_required()
def category(request, name=None):
    c = get_object_or_404(Category, name=name)
    posts = Post.objects.filter(category=c).order_by("-published_date")
    context = {'posts': posts,}
    context.update(get_categories(request))
    return render(request, 'mainapp/library.html', context=context)


@login_required()
def search(request):
    query = request.GET.get('query')

    post_blog_list = Post.objects.filter(Q(content__icontains=query) | Q(title__icontains=query)).order_by("-published_date")
    my_posts_list = LibText.objects.filter(content__icontains=query)
    context = {'post_blog_list': post_blog_list,
               'my_posts_list': my_posts_list
               }
    context.update(get_categories(request))
    return render(request, 'mainapp/library.html', context=context)


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
    context.update(get_categories(request))
    return render(request, 'mainapp/create.html', context=context)