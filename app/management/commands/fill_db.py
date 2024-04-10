from django.core.management.base import BaseCommand, CommandError
from app.models import *
from askme_novikov.settings import STATICFILES_DIRS
from random import randint
from itertools import islice

def save_batch(method, generator, batch_size):
    i = 0
    while True:
        batch = list(islice(generator, batch_size))
        if not batch:
            break
        method(batch, batch_size)
        i += 1

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ratio", nargs="+", type=int)

    def handle(self, *args, **options):
        ratio = options.get("ratio", [-1])[0]
        if ratio > 0:
            profiles_number = ratio
            questions_number = 10 * ratio
            answers_number = 100 * ratio
            tags_number = ratio
            ratings_number = 100 * ratio

            batch_size = 10000

            users_gen = (
                User(
                    username=f"nickname_{i}",
                    email=f"user_{i}@gmail.com",
                    password=f"password_{i}",
                ) for i in range(profiles_number)
            )
            save_batch(User.objects.bulk_create, users_gen, batch_size)
            print("Users saved")

            def profile_gen():
                i = 0
                while True:
                    users_batch = User.objects
                    users_batch = users_batch.filter(username__contains="nickname")
                    users_batch = users_batch[i*batch_size:(i + 1)*batch_size]
                    if not users_batch:
                        break
                    for j in range(min(batch_size, profiles_number - batch_size * i)):
                        profile = Profile(
                            user=users_batch[j],
                            avatar=(STATICFILES_DIRS[0] / "img.jpg").as_posix()
                        )
                        yield profile
                    i += 1
            save_batch(Profile.objects.bulk_create, profile_gen(), batch_size)
            print("Profiles saved")

            tags_gen = (
                Tag(
                    name=f"tag_{i}"
                ) for i in range(tags_number)
            )
            save_batch(Tag.objects.bulk_create, tags_gen, batch_size)
            print("Tages saved")

            def questions_gen():
                i = 0
                while True:
                    profiles_batch = Profile.objects
                    profiles_batch = profiles_batch.get_queryset()
                    profiles_batch = profiles_batch[int(i*batch_size/10):int((i + 1)*batch_size/10)]
                    tags_batch = Tag.objects
                    tags_batch = tags_batch.get_queryset()
                    tags_batch = tags_batch[int(i*batch_size/10):int((i + 1)*batch_size/10)]
                    if not profiles_batch:
                        break
                    for j in range(min(batch_size, questions_number - batch_size * i)):
                        question = Question(
                            title=f"Question title {i * batch_size + j}",
                            text=f"Text for question {i * batch_size + j} " * 10,
                            author=profiles_batch[int(j / 10)],
                        )
                        yield question
                    i += 1
            save_batch(Question.objects.bulk_create, questions_gen(), batch_size)
            print("Questions saved")

            def question_tag_gen():
                i = 0
                while True:
                    questions_batch = Question.objects
                    questions_batch = questions_batch.get_queryset()
                    questions_batch = questions_batch[i*batch_size:(i + 1)*batch_size]
                    tags_batch = Tag.objects
                    tags_batch = tags_batch.get_queryset()
                    tags_batch = tags_batch[int(i*batch_size/10):int((i + 1)*batch_size/10)]
                    if not(questions_batch and tags_batch):
                        break
                    for j in range(min(batch_size, questions_number - i*batch_size)):
                        for tag in tags_batch[int(j/10):int(j/10) + 3]:
                            question_tag = Question.tags.through(question=questions_batch[j], tag=tag)
                            yield question_tag
                    i += 1
            save_batch(Question.tags.through.objects.bulk_create, question_tag_gen(), batch_size)
            print("Tags attached to questions")

            def answers_gen():
                i = 0
                while True:
                    profiles_batch = Profile.objects
                    profiles_batch = profiles_batch.get_queryset()
                    profiles_batch = profiles_batch[int(i*batch_size/100):int((i + 1)*batch_size/100)]
                    questions_batch = Question.objects
                    questions_batch = questions_batch.get_queryset()
                    questions_batch = questions_batch[int(i*batch_size/10):int((i + 1)*batch_size/10)]
                    if not(profiles_batch and questions_batch):
                        break
                    for j in range(min(batch_size, answers_number - batch_size*i)):
                        answer = Answer(
                            text=f"Text for answer {i * batch_size + j} " * 10,
                            author=profiles_batch[int(j/100)],
                            question=questions_batch[int(j/10)],
                        )
                        yield answer
                    i += 1
            save_batch(Answer.objects.bulk_create, answers_gen(), batch_size)
            print("Answers saved")

            def question_ratings_gen():
                i = 0
                while True:
                    questions_batch = Question.objects
                    questions_batch = questions_batch.get_queryset()
                    questions_batch = questions_batch[int(i*batch_size/10):int((i + 1)*batch_size/10)]
                    profiles_batch = Profile.objects
                    profiles_batch = profiles_batch.get_queryset()
                    profiles_batch = profiles_batch[int(i*batch_size/100):int((i + 1)*batch_size/100)]
                    if not(questions_batch and profiles_batch):
                        break
                    for j in range(min(batch_size, ratings_number - batch_size*i)):
                        question_rating = QuestionsRating(
                            value=1 if randint(0,1) == 1 else -1,
                            question=questions_batch[int(j/10)],
                            author=profiles_batch[int(j/100)],
                        )
                        yield question_rating
                    i += 1
            save_batch(QuestionsRating.objects.bulk_create, question_ratings_gen(), batch_size)
            print("Question ratings saved")
            
            i = 0
            while True:
                questions_batch = Question.objects
                questions_batch = questions_batch.get_queryset()
                questions_list = questions_batch[i*batch_size:(i + 1)*batch_size]
                if not(questions_list):
                    break
                for question in questions_list:
                    question.rating = Question.objects.get_rating(id=question.id)
                Question.objects.bulk_update(questions_list, ["rating"])
                i += 1
            print("Questions rating calculated")

            def answer_ratings_gen():
                i = 0
                while True:
                    answers_batch = Answer.objects
                    answers_batch = answers_batch.get_queryset()
                    answers_batch = answers_batch[i*batch_size:(i + 1)*batch_size]
                    profiles_batch = Profile.objects
                    profiles_batch = profiles_batch.get_queryset()
                    profiles_batch = profiles_batch[int(i*batch_size/100):int((i + 1)*batch_size/100)]
                    if not(answers_batch and profiles_batch):
                        break
                    for j in range(min(batch_size, ratings_number - batch_size*i)):
                        answers_rating = AnswersRating(
                            value=1 if randint(0,1) == 1 else -1,
                            answer=answers_batch[j],
                            author=profiles_batch[int(j/100)],
                        )
                        yield answers_rating
                    i += 1
            save_batch(AnswersRating.objects.bulk_create, answer_ratings_gen(), batch_size)
            print("Answer ratings saved")

            i = 0
            while True:
                answers_batch = Answer.objects
                answers_batch = answers_batch.get_queryset()
                answers_list = answers_batch[i*batch_size:(i + 1)*batch_size]
                if not(answers_list):
                    break
                for answer in answers_list:
                    answer.rating = Answer.objects.get_rating(id=answer.id)
                Answer.objects.bulk_update(answers_list, ["rating"])
                i += 1
            print("Answers rating calculated")