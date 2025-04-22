from django.urls import path
from . import views

app_name = "quiz"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("<int:quiz_id>/", views.question, name="question"),
    path("<int:quiz_id>/results", views.results, name="results"),
]