# from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from random import randint

# Create your views here.

QUESTIONS = [
    {
        "id": i,
        "title": f"Question {i}",
        "text": f"This is question number {i}",
        "tags": [
            f"tag{randint(0,10)}",
            f"tag{randint(0,10)}",
            f"tag{randint(0,10)}",
        ],
        "answers": [
        {
            "id": i,
            "text": f"this is answer number {i}",
        } for i in range(10)
        ],
    } for i in range(100)
]

def index(request):
    return render(request, "index.html", {"questions": paginate(QUESTIONS, request)})

def hot_questions(request):
    return render(request, "hot_questions.html", {"questions": paginate(QUESTIONS, request)})

def settings(request):
    return render(request, "settings.html")

def logout(request):
    return render(request, "index.html", {"questions": paginate(QUESTIONS, request)})

def tag(request, tag):
    questions = []
    for i in range(len(QUESTIONS)):
        if tag in QUESTIONS[i].get("tags"):
            questions.append(QUESTIONS[i])
    return render(request, "tag.html", {
        "questions": paginate(questions, request),
        "tag": tag,
        }
    )

def ask(request):
    return render(request, "ask.html")

def question(request, question_id):
    return render(request, "question.html", {
        "question": QUESTIONS[int(question_id)],
        "answers": paginate(QUESTIONS[int(question_id)].get("answers"), request),
        }
    )

def login(request):
    return render(request, "login.html")

def signup(request):
    return render(request, "signup.html")

def paginate(obj_list, request, per_page=5):
    page_num = request.GET.get("page", 1)
    paginator = Paginator(obj_list, per_page)
    page_obj = paginator.page(page_num)
    return page_obj