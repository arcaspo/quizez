from django.shortcuts import get_object_or_404, render, get_list_or_404
from .models import Quiz
from .models import Question
from .models import Answer
from .models import Result

# Create your views here.
def dashboard(request):
    # get quizzes that are close to being due
    due_quiz_list = Quiz.objects.order_by("-due_date")

    # create the context that gets sent to the html file
    context = {"due_quiz_list": due_quiz_list}

    # render the html file
    return render(request, "quiz/dashboard.html", context)

def question(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    # results = get_list_or_404(Result, quiz=quiz)
    questions = get_list_or_404(Question, quiz=quiz)

    next_question: Question = None
    # Find next question that hasnt been answered
    for question in questions:
        if not Result.objects.filter(quiz=quiz, question=question).exists():
            if next_question is None:
                next_question = question

            elif next_question.order > question.order:
                next_question = question

    return render(request, "quiz/question.html", {"quiz": quiz, "question": next_question})