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

class ProfileManager(models.Manager):
    def get_by_user_id(self, user_id):
        return Profile.objects.filter(user__id=user_id).first()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    avatar = models.ImageField(upload_to="avatars", default="avatars/avatar.png")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProfileManager()

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
        rating_sum = QuestionsRating.objects.filter(question__id=question_id).aggregate(sum=models.Sum("value")).get("sum")
        return rating_sum if rating_sum else 0 

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

class QuestionRatingManager(models.Manager):
    def like(self, profile, question):
        rating = self.filter(author=profile).filter(question=question).first()
        if rating:
            if rating.value == -1:
                rating.value = 1
                rating.save()
            else:
                rating.delete()
        else:
            rating = QuestionsRating.objects.create(
                value=1,
                question=question,
                author=profile,
            )
        question.rating = Question.objects.get_rating(question.id)
        question.save()

    def dislike(self, profile, question):
        rating = self.filter(author=profile).filter(question=question).first()
        if rating:
            if rating.value == 1:
                rating.value = -1
                rating.save()
            else:
                rating.delete()
        else:
            rating = QuestionsRating.objects.create(
                value=-1,
                question=question,
                author=profile,
            )
        question.rating = Question.objects.get_rating(question.id)
        question.save()
    
    def get_liked_disliked_questions(self, profile):
        ratings = self.filter(author=profile).all()
        liked_questions = []
        disliked_questions = []
        for rating in ratings:
            if rating.value == 1:
                liked_questions.append(rating.question)
            elif rating.value == -1:
                disliked_questions.append(rating.question)
        return [liked_questions, disliked_questions]

    def check_liked_disliked_question(self, profile, question_id):
        rating = self.filter(author=profile).filter(question__id=question_id).first()
        question_liked = False
        question_disliked = False
        if rating:
            if rating.value == 1:
                question_liked = True
            elif rating.value == -1:
                question_disliked = True
        return [question_liked, question_disliked]

class QuestionsRating(models.Model):
    VALUE_CHOICES = [
        (1, 1),
        (-1, -1),
    ]
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    objects = QuestionRatingManager()

    class Meta:
        unique_together = ("question", "author")
    
    def __str__(self):
        return f"Rating {self.value} for {self.question} from {self.author}"

class AnswerManager(models.Manager):
    def get_best_for_question(self, question_id):
        return self.filter(question_id=question_id).order_by("rating").reverse()
    
    def get_rating(self, answer_id):
        rating_sum = AnswersRating.objects.filter(answer__id=answer_id).aggregate(sum=models.Sum("value")).get("sum")
        return rating_sum if rating_sum else 0

class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AnswerManager()

    def __str__(self):
        return f"answer for {self.question} from {self.author}"

class AnswersRatingManager(models.Manager):
    def like(self, profile, answer):
        rating = self.filter(author=profile).filter(answer=answer).first()
        if rating:
            if rating.value == -1:
                rating.value = 1
                rating.save()
            else:
                rating.delete()
        else:
            rating = self.create(
                value=1,
                answer=answer,
                author=profile,
            )
        answer.rating = Answer.objects.get_rating(answer.id)
        answer.save()

    def dislike(self, profile, answer):
        rating = self.filter(author=profile).filter(answer=answer).first()
        if rating:
            if rating.value == 1:
                rating.value = -1
                rating.save()
            else:
                rating.delete()
        else:
            rating = self.create(
                value=-1,
                answer=answer,
                author=profile,
            )
        answer.rating = Answer.objects.get_rating(answer.id)
        answer.save()

    def get_liked_disliked_answers(self, profile):
        ratings = self.filter(author=profile).all()
        liked_answers = []
        disliked_answers = []
        for rating in ratings:
            if rating.value == 1:
                liked_answers.append(rating.answer)
            elif rating.value == -1:
                disliked_answers.append(rating.answer)
        return [liked_answers, disliked_answers]

class AnswersRating(models.Model):
    VALUE_CHOICES = [
        (1, 1),
        (-1, -1),
    ]
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    
    objects = AnswersRatingManager()

    class Meta:
        unique_together = ("answer", "author")

    def __str__(self):
        return f"Rating {self.value} for {self.answer} from {self.author}"