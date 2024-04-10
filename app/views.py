from django.http.response import HttpResponseNotFound
from django.shortcuts import render
from django.core.paginator import Paginator
from app.models import *
from random import randint

from app import models

# Create your views here.

def index(request):
    questions = models.Question.objects.get_new()
    question_list = paginate(questions, request, per_page=20)
    context = {"questions": question_list}
    return render(request, "index.html", context)

def hot_questions(request):
    questions = models.Question.objects.get_hot()
    question_list = paginate(questions, request, per_page=20)
    context = {"questions": question_list}
    return render(request, "hot_questions.html", context)

def settings(request):
    return render(request, "settings.html")

def logout(request):
    questions = Question.objects.get_new()
    context = {"questions": paginate(questions, request, per_page=20)}
    return render(request, "index.html", context)

def tag(request, tag_name):
    questions = Question.objects.get_by_tag(tag_name)
    if not(questions):
        return HttpResponseNotFound("page no found")
    questions_list = paginate(questions, request, per_page=20)
    context = {
        "questions": questions_list,
        "tag": tag_name,
    }
    return render(request, "tag.html", context)

def ask(request):
    return render(request, "ask.html")

def question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponseNotFound("page not found")
    answers = Answer.objects.get_best_for_question(question_id)
    answers_list = paginate(answers, request, per_page=30)
    context = {
        "question": question,
        "answers": answers_list,
    }
    return render(request, "question.html", context)

def login(request):
    return render(request, "login.html")

def signup(request):
    return render(request, "signup.html")

def paginate(query_set, request, per_page=10):
    page_num = request.GET.get("page", "1")
    paginator = Paginator(query_set, per_page)
    if page_num > "0" and page_num <= str(paginator.num_pages):
        page_obj = paginator.page(page_num)
    else:
        page_obj = paginator.page(1)
    return page_obj