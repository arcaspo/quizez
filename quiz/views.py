from django.forms import formset_factory
from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from .models import Quiz, Question, Answer, Result
from .forms import QuestionForm, CreateQuizForm, CreateQuestionForm, CreateAnswerForm

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
        # Redirect back to the dashboard once quiz is submitted
        return redirect("quiz:dashboard")

    else:
        # Get the quiz and the results for the user that completed it
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        results = Result.objects.filter(quiz=quiz, user=request.user)

        num_correct = sum(1 for result in results if result.is_correct)
        percentage_correct = (num_correct / quiz.number_of_questions) * 100

        # Render the results template with the quiz and results data
        return render(request, "quiz/results.html", {
            "quiz": quiz,
            "results": results,
            "num_correct": num_correct,
            "percentage_correct": percentage_correct,
        })

def create_quiz(request):
    if request.method == "POST":
        # Save the quiz and redirect to the edit page so it can be edited
        form = CreateQuizForm(request.POST)
        if form.is_valid:
            quiz = form.save()
            redirect("quiz:edit_quiz", quiz_id=quiz.id)

    else:
        # Create the empty quiz form and send it to the template to render
        quiz_form = CreateQuizForm()
        render(request, "quiz/create_quiz.html", {"quiz_form": quiz_form})

def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    if request.method == "POST":
        if "new_question" in request.POST:
            question = Question.objects.create(
                quiz=quiz,
                question_text="",
                order=quiz.number_of_questions + 1,
                editing=True,
            )
            question_form = CreateQuestionForm(prefix="question", instance=question)

        elif "submit_question" in request.POST:
            question_form = CreateQuestionForm(request.POST, prefix="question")
            if question_form.is_valid():
                # Save the question and redirect to the edit page
                question = question_form.save(commit=False)
                question.editing = False
                question.save()

        elif "new_answer" in request.POST:
            # TODO somehow fetch which question this answer belongs to from the request 
            #Answer = Answer.objects.create(
            #    question=
            #)
            pass

        elif "submit_answer" in request.POST:
            answer_form = CreateAnswerForm(request.POST, prefix="answer")
            if answer_form.is_valid():
                # Save the question and redirect to the edit page
                answer = answer_form.save(commit=False)
                answer.editing = False
                question.save()

        # Once all the forms are processed or new ones are created, render the template with the updated context
        questions = Question.objects.filter(quiz=quiz)
        context = {
            "quiz": quiz,
            "questions": questions,
            "question_form": question_form,
            "answer_form": answer_form,
        }
        return render(request, "quiz/edit_quiz.html", context)
        
    else:
        # If the request isn't a POST, don't provide a form for the question as we haven't added one yet
        context = {
            "quiz": quiz, 
            "questions": Question.objects.filter(quiz=quiz),
        }
        return render(request, "quiz/edit_quiz.html", context)

    # Create the emtpy forms with prefixes so they can be identified in POST request
    question_form = CreateQuestionForm(prefix="question")
    answer_form = CreateAnswerForm(prefix="answer")

