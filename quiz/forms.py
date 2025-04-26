from django import forms
from .models import Answer, Quiz, Question
from django.forms import ModelForm

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

class CreateQuizForm(ModelForm):
    class Meta:
        model = Quiz
        fields = ['quiz_name', 'due_date', 'quiz_description']

class CreateQuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'order']

class CreateAnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = ['choice_text', 'correct', 'order']