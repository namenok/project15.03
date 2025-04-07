
from django.urls import path
from . import views



app_name = 'mainapp'

urlpatterns = [
    path('', views.index, name='index'),  # /first
    path('home/', views.home, name='home'),
    path('checkme/', views.survey_view, name='checkme'),
    # path('successful/', views.survey_thanks, name='survey_thanks'),

    path('calendar/', views.calendar, name='calendar'),
    path('post/<str:id>', views.post, name='post'),
    # path('new_entry/', views.new_entry, name='new_entry'),

    # path('image_uploads/', views.image_upload, name='image_uploads'),


    path('categories/', views.library_view, name='library_category_list'),
    path('category/<slug:slug>/', views.library_view, name='library_posts_by_category'),

    path('search/', views.search, name='search'),
    path('create/', views.create, name='create'),

    # path('lib_user_post/', views.lib_user_post, name='lib_user_post'),

    path('write/', views.daily_post_view, name='daily_post'),  
    path('history/', views.post_history_view, name='post_history'),


]