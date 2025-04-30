from django.urls import path
from . import views

app_name = "quiz"
urlpatterns = [
    path("", views.student_dashboard, name="student_dashboard"),
    path("<int:quiz_id>/", views.question, name="question"),
    path("<int:quiz_id>/results", views.results, name="results"),
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/<int:quiz_id>", views.edit_quiz, name="edit_quiz")
]