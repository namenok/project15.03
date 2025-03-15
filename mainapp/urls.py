
from django.urls import path
from . import views



app_name = 'mainapp'

urlpatterns = [
    path('index', views.index, name='index'),  # /first
    path('', views.home, name='home'),
    path('checkme', views.checkme, name='checkme'),
    path('library', views.library, name='library'),
    path('calendar', views.calendar, name='calendar'),

    path('new_entry', views.new_entry, name='new_entry'),

    path('image_uploads', views.image_upload, name='image_uploads'),
    path('post/<int:id>', views.post, name='post'),

    path('category/<str:name>', views.category, name='category'),
    path('search', views.search, name='search'),
    path('create', views.create, name='create'),
]