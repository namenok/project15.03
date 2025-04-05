
from django.urls import path
from . import views



app_name = 'mainapp'

urlpatterns = [
    path('', views.index, name='index'),  # /first
    path('home/', views.home, name='home'),
    path('checkme/', views.checkme, name='checkme'),

    path('calendar/', views.calendar, name='calendar'),

    path('new_entry/', views.new_entry, name='new_entry'),

    path('image_uploads/', views.image_upload, name='image_uploads'),
    path('post/<str:id>', views.post, name='post'),

    path('categories/', views.library_view, name='library_category_list'),
    path('category/<slug:slug>/', views.library_view, name='library_posts_by_category'),

    path('search/', views.search, name='search'),
    path('create/', views.create, name='create'),


]