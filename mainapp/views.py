from dbm.ndbm import library
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .forms import EntryForm, FotoForm, PostForm
from django.contrib.auth.decorators import login_required
from .models import Category, Post, LibText, Teg
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


@login_required()
def home(request):
    title = "це мій домашній кабінет тут записую думки та картикни"
    context = {"title":title,}
    return render(request, 'mainapp/home.html', context=context)


@login_required()
def checkme(request):
    return render(request, 'mainapp/checkme.html')



@login_required()
def post(request, id=None):
    post = get_object_or_404(Post, title=id)
    context = {"post": post, }
    # context.update(get_categories(request))
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