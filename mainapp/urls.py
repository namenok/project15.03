from django.urls import path
from . import views


app_name = "mainapp"

urlpatterns = [
    path("", views.index, name="index"),  # /first
    path("checkme/", views.survey_view, name="checkme"),
    path("survey/history/", views.survey_history, name="survey_history"),
    path("calendar/", views.calendar_combined_view, name="calendar_combined"),
    path("library/history/", views.library_users_history, name="library_history"),
    path("categories/", views.categories_overview, name="library_category_list"),
    path(
        "category/<slug:slug>/",
        views.category_list_view,
        name="library_posts_by_category",
    ),
    path("search/", views.search, name="search"),
    path("create/", views.create, name="create"),
    path("post/<str:id>", views.post, name="post"),
    path("write/", views.daily_post_view, name="daily_post"),
    path("history/", views.post_history_view, name="post_history"),
    path("analytics/", views.monthly_analytics_view, name="monthly_analytics"),
    path("chat/", views.chat_page, name="chat_page"),
    path("home/", views.home, name="home"),
]
