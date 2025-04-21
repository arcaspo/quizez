from django import forms
from .models import Answer

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