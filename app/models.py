from django.contrib.auth.models import User
from django.db import models

# Create your models here.

# Пользователь – электронная почта, никнейм, пароль, аватарка, дата регистрации, рейтинг.
# Вопрос – заголовок, содержание, автор, дата создания, теги, рейтинг.
# Ответ – содержание, автор, дата написания, флаг правильного ответа, рейтинг.
# Тег – слово тега.

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    avatar = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_short_name()

class QuestionManager(models.Manager):
    def get_new(self):
        return self.order_by("created_at").reverse()
    
    def get_hot(self):
        return self.order_by("rating").reverse()
    
    def get_by_tag(self, tag_name):
        return self.filter(tags__name=tag_name)
    
    def get_rating(self, question_id):
        rating_sum = QuestionsRating.objects.filter(question__id=question_id).aggregate(sum=models.Sum("value"))
        return rating_sum.get("sum", 0)

class Question(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField(max_length=500)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = QuestionManager()

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

    class Meta:
        unique_together = ("question", "author")
    
    def __str__(self):
        return f"Rating {self.value} for {self.question} from {self.author}"

class AnswerManager(models.Manager):
    def get_best_for_question(self, question_id):
        return self.filter(question_id=question_id).order_by("rating").reverse()
    
    def get_rating(self, answer_id):
        rating_sum = AnswersRating.objects.filter(answer__id=answer_id).aggregate(sum=models.Sum("value"))
        return rating_sum.get("sum", 0)

class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AnswerManager()

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
    
    class Meta:
        unique_together = ("answer", "author")

    def __str__(self):
        return f"Rating {self.value} for {self.answer} from {self.author}"