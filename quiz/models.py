from django.db import models

class Quiz(models.Model):
    quiz_name = models.CharField(max_length=200)
    due_date = models.DateTimeField("data due")
    num_questions = models.IntegerField()

    def __str__(self):
        return self.quiz_name

# Create your models here.
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True)
    question_text = models.CharField(max_length=200)
    multiple_answers = models.BooleanField()

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.question