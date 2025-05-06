from django.forms import formset_factory
from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from .models import Quiz, Question, Answer, Result
from .forms import QuestionForm, EditQuizForm, EditQuestionFormSet, EditAnswerFormSet, SignupForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group

def is_teacher(user):
    return user.groups.filter(name='teacher').exists()

def is_student(user):
    return user.groups.filter(name='student').exists()

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Get the selected user type
            user_type = form.cleaned_data['user_type']

            # Assign the user to the correct group
            group = Group.objects.get(name=user_type)  # Ensure the group exists in the database
            user.groups.add(group)
            
            return redirect('quiz:login')  # Redirect to login after signup
    else:
        form = SignupForm()
    return render(request, 'quiz/signup.html', {"form": form})

def homepage(request):
    return render(request, 'quiz/homepage.html')

@login_required
def dashboard(request):
    # If we're authenticated as a teacher redirect to the teacher_dashboard
    # If we're authenticated as a student redirect to the student_dashboard
    if is_teacher(request.user):
        return redirect('quiz:teacher_dashboard')
    elif is_student(request.user):
        return redirect('quiz:student_dashboard')

@user_passes_test(is_student)
def student_dashboard(request):
    # get quizzes that are close to being due
    due_quiz_list = Quiz.objects.order_by("-due_date")

    # create the context that gets sent to the html file
    context = {"due_quiz_list": due_quiz_list}

    # render the html file
    return render(request, "quiz/student_dashboard.html", context)

@user_passes_test(is_teacher)
def teacher_dashboard(request):
    if request.method == "POST":
        if "add_quiz" in request.POST:
            # If create quiz button pressed then create a empty quiz and redirect to edit quiz page
            quiz = Quiz.objects.create(
                quiz_name="Enter Quiz Name",
                due_date=None,
                quiz_description="Enter Quiz Description",
                editing=True
            )
            return redirect('quiz:edit_quiz', quiz_id=quiz.pk)

    # temporarily order by reverse due date
    quiz_list = Quiz.objects.order_by("-due_date")
    context = {"quiz_list": quiz_list}

    return render(request, "quiz/teacher_dashboard.html", context)

@login_required
def question(request, quiz_id):
    # Get the quiz and its questions
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = get_list_or_404(Question, quiz=quiz)

    if request.method == "POST":
        if "exit" in request.POST:
            if is_teacher(request.user):
                return redirect('quiz:edit_quiz', quiz_id=quiz_id)
            
            else:
                return redirect('quiz:dashboard')

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
        # If theres no more questions, Show a finished page with stats
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

        if is_teacher(request.user):
            # delete the results if it is a teacher previewing the quiz and redirect back to edit page
            quiz = get_object_or_404(Quiz, pk=quiz_id)
            Result.objects.filter(quiz=quiz, user=request.user).delete()
            return redirect("quiz:edit_quiz", quiz_id=quiz_id)

        else:
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

def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    if request.method == 'POST':
        answers_valid = True
        answer_formsets = {}
        question_formset = EditQuestionFormSet(request.POST, instance=quiz, prefix="question_formset")
        quiz_form = EditQuizForm(request.POST, instance=quiz, prefix="quiz_form")
        if quiz_form.is_valid():
            quiz_form.save()

            i = 0
            if question_formset.is_valid():
                for question_form in question_formset:
                    question = question_form.save(commit=False)
                    question.quiz = quiz
                    question.save()

                    answer_formset = EditAnswerFormSet(request.POST, instance=question, prefix=f'{i}_answer_formset')
                    if answer_formset.is_valid():
                        for answer_form in answer_formset:
                            answer = answer_form.save(commit=False)
                            answer.question = question
                            answer.save()
                    else:
                        answers_valid = False
                        print("invalid answer formset")
                        print(answer_formset.errors)
                        print(answer_formset)
                    i += 1

                if answers_valid:
                    return redirect('quiz:dashboard')

            else:
                print(question_formset.errors)
        else:
            print(quiz_form.errors)
        
        if not answers_valid:
            # Create the answer_formsets manually if the other validations fail
            i = 0
            for question in quiz.question_set.all():
                answer_formsets[f"{i}_answer_formset"] = EditAnswerFormSet(request.POST, instance=question, prefix=f"{i}_answer_formset")
                i += 1

    else:
        quiz_form = EditQuizForm(instance=quiz, prefix="quiz_form")
        question_formset = EditQuestionFormSet(instance=quiz, prefix='question_formset')
        answer_formsets = {}

        i = 0
        for question in quiz.question_set.all():
            answer_formsets[f"{i}_answer_formset"] = EditAnswerFormSet(instance=question, prefix=f"{i}_answer_formset")
            i += 1

    # Generate an empty answer formset for the empty question form
    empty_question = Question(quiz=quiz)  # Create a dummy question instance
    empty_answer_formset = EditAnswerFormSet(instance=empty_question, prefix='__prefix__')

    context = {
        'quiz': quiz,
        'quiz_form': quiz_form,
        'question_formset': question_formset,
        'answer_formsets': answer_formsets,
        'empty_answer_formset': empty_answer_formset,  # Pass the empty answer formset
    }

    return render(request, 'quiz/edit_quiz.html', context)