from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "quiz"
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("dashboard/student", views.student_dashboard, name="student_dashboard"),
    path("<int:quiz_id>", views.question, name="question"),
    path("<int:quiz_id>/results", views.results, name="results"),
    path("dashboard/teacher", views.teacher_dashboard, name="teacher_dashboard"),
    path("edit/<int:quiz_id>", views.edit_quiz, name="edit_quiz"),

    path('login/', LoginView.as_view(template_name='quiz/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=''), name='logout'),
    path('signup/', views.signup, name='signup'),
]