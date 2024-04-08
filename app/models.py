from django.contrib.auth.models import User
from django.db import models

# Create your models here.

# Пользователь – электронная почта, никнейм, пароль, аватарка, дата регистрации, рейтинг.
# Вопрос – заголовок, содержание, автор, дата создания, теги, рейтинг.
# Ответ – содержание, автор, дата написания, флаг правильного ответа, рейтинг.
# Тег – слово тега.

class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_username()

class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class QuestionsRating(models.Model):
    VALUE_CHOICES = [
        (1, 1),
        (-1, -1),
    ]
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Rating {self.value} for {self.question} from {self.author}"

class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"answer for {self.question} from {self.author}"

class AnswersRating(models.Model):
    VALUE_CHOICES = [
        (1, 1),
        (-1, -1),
    ]
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Rating {self.value} for {self.answer} from {self.author}"