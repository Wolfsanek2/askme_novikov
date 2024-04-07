from django.contrib.auth.models import User
from django.db import models

# Create your models here.

# Пользователь – электронная почта, никнейм, пароль, аватарка, дата регистрации, рейтинг.
# Вопрос – заголовок, содержание, автор, дата создания, теги, рейтинг.
# Ответ – содержание, автор, дата написания, флаг правильного ответа, рейтинг.
# Тег – слово тега.

class Tags(models.Model):
    name = models.CharField(max_length=255)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    nickname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    avatar = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(Profile)
    tags = models.ManyToManyField(Tags)
    created_at = models.DateTimeField(auto_now_add=True)

class QuestionsRating(models.Model):
    VALUE_CHOICES = [
        (1, 1),
        (-1, -1),
    ]
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Profile)
    created_ar = models.DateTimeField(auto_now_add=True)

class AnswersRating(models.Model):
    VALUE_CHOICES = [
        (1, 1),
        (-1, -1),
    ]
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    answer = models.ForeignKey(Answer)
    author = models.ForeignKey(Profile)