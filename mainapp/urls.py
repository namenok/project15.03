from django.urls import path
from . import views


app_name = "mainapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("checkme/", views.survey_view, name="checkme"),
    path("survey/history/", views.survey_history, name="survey_history"),
    path("calendar/", views.calendar_combined_view, name="calendar_combined"),

    path("write/", views.daily_post_view, name="daily_post"),
    path("history/", views.post_history_view, name="post_history"),
    path("analytics/", views.monthly_analytics_view, name="monthly_analytics"),

    path("chat/", views.chat_page, name="chat_page"),
    path("home/", views.home, name="home"),

    path('spotify-search/', views.spotify_search, name='spotify_search'),
    path("spotify/login/", views.spotify_login, name="spotify_login"),
    path("spotify/callback/", views.spotify_callback, name="spotify_callback"),
]
