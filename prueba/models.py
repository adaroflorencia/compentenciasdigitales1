from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):

    name = models.CharField(max_length=20, unique=True)
    users = models.ManyToManyField(User, related_name="roles")

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='topics')

    def __str__(self):
        return self.name

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text

class Answer(models.Model):
    session_id = models.CharField(max_length=255)  # ID de sesión para relacionar respuestas
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    option = models.ForeignKey('Option', on_delete=models.CASCADE)

    def __str__(self):
        return f"Session: {self.session_id} - {self.question.text} - {self.option.text}"

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    score = models.IntegerField(default=1)

    def __str__(self):
        return self.text

class TopicResult(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=32)
    score = models.FloatField(default=0)
    level = models.CharField(max_length=10, default='A1')
    total_questions = models.IntegerField(default=0)

    class Meta:
        unique_together = ('topic', 'session_id')

    def __str__(self):
        if self.session_id:
            return f"{self.topic.name} - Session {self.session_id[:8]}"
        return f"{self.topic.name}"