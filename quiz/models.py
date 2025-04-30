from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    quiz_name = models.CharField(max_length=200)
    due_date = models.DateTimeField("due date", blank=True, null=True)
    quiz_description = models.TextField(blank=True, null=True)
    editing = models.BooleanField(default=False)

    def __str__(self):
        return self.quiz_name
    
    # Property to get count dynamically
    @property
    def number_of_questions(self):
        return self.question_set.count()

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    editing = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text
    
    class Meta:
        ordering = ['order']  # Order by the 'order' field

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    editing = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']  # Order by the 'order' field

    def __str__(self):
        return self.choice_text
    
class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # Associate result with a user
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    @property
    def is_correct(self):
        return self.answer.correct
    
    @property
    def correct_answer(self):
        return self.question.answer_set.filter(correct=True).first()