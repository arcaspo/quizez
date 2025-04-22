from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from .models import Quiz
from .models import Question
from .models import Answer
from .models import Result
from .forms import QuestionForm

# Create your views here.
def dashboard(request):
    # get quizzes that are close to being due
    due_quiz_list = Quiz.objects.order_by("-due_date")

    # create the context that gets sent to the html file
    context = {"due_quiz_list": due_quiz_list}

    # render the html file
    return render(request, "quiz/dashboard.html", context)

def question(request, quiz_id):
    # Get the quiz and its questions
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = get_list_or_404(Question, quiz=quiz)

    if request.method == "POST":
        # Get the question that was answered
        question_id = request.POST.get('submit')
        question = get_object_or_404(Question, pk=question_id)

        # Create a form instance with the data from the request (what the user selected)
        form = QuestionForm(question, request.POST)

        if form.is_valid():
            # Get the selected answer
            selected_answer_id = form.cleaned_data['answer']

            if Result.objects.filter(quiz=quiz, question=question, user=request.user).exists():
                # If the answer already exists, update it
                result = Result.objects.get(quiz=quiz, question=question, user=request.user)
                result.answer = get_object_or_404(Answer, pk=selected_answer_id)
                result.save()
            else:
                # Save answer to a new result model
                Result.objects.create(
                    user=request.user,  # Assuming you have user authentication
                    quiz=quiz,
                    question=question,
                    answer=get_object_or_404(Answer, pk=selected_answer_id)
                )

    # Get the next question to be displayed
    next_question = get_next_question(quiz, questions, request.user)
    print(quiz.number_of_questions)

    if next_question:
        # If theres another question create a form for it and render the template
        form = QuestionForm(next_question)
        return render(request, "quiz/question.html", {"quiz": quiz, "question": next_question, "form": form})

    else:
        # If theres no more questions, Show a finished page with stats (not done yet)
        return redirect("quiz:results", quiz_id=quiz_id)

def get_next_question(quiz, questions, user):
    next_question: Question = None
    # Find next question that hasnt been answered
    for question in questions:
        if not Result.objects.filter(quiz=quiz, question=question, user=user).exists():
            if next_question is None:
                next_question = question

            elif next_question.order > question.order:
                next_question = question

    return next_question

def results(request, quiz_id):
    if request.method == "POST":
        return redirect("quiz:dashboard")

    else:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        results = Result.objects.filter(quiz=quiz, user=request.user)

        num_correct = sum(1 for result in results if result.is_correct)
        percentage_correct = (num_correct / quiz.number_of_questions) * 100

        return render(request, "quiz/results.html", {
            "quiz": quiz,
            "results": results,
            "num_correct": num_correct,
            "percentage_correct": percentage_correct,
        })