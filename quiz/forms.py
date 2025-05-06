from django import forms
from .models import Answer, Quiz, Question
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student')
    ]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'user_type']

class QuestionForm(forms.Form):
    answer = forms.ChoiceField(
        widget=forms.RadioSelect,  # Use radio buttons for choices
        label="Select an answer",
    )
    question_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate choices based on the given question
        self.fields['answer'].choices = [
            (answer.id, answer.choice_text) for answer in Answer.objects.filter(question=question)
        ]
        self.fields['question_id'].initial = question.id

class EditQuizForm(ModelForm):
    class Meta:
        model = Quiz
        fields = ['quiz_name', 'due_date', 'quiz_description']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

EditQuestionFormSet = inlineformset_factory(Quiz, Question, fields=('question_text',), extra=0)
EditAnswerFormSet = inlineformset_factory(Question, Answer, fields=('choice_text', 'correct'), extra=0)