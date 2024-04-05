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
        "likes": randint(0,10),
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
        "answers_number": 10,
    } for i in range(100)
]

def index(request):
    return render(request, "index.html", {"questions": paginate(QUESTIONS, request, per_page=20)})

def hot_questions(request):
    return render(request, "hot_questions.html", {"questions": paginate(QUESTIONS, request, per_page=20)})

def settings(request):
    return render(request, "settings.html")

def logout(request):
    return render(request, "index.html", {"questions": paginate(QUESTIONS, request, per_page=20)})

def tag(request, tag):
    questions = []
    for i in range(len(QUESTIONS)):
        if tag in QUESTIONS[i].get("tags"):
            questions.append(QUESTIONS[i])
    return render(request, "tag.html", {
        "questions": paginate(questions, request, per_page=20),
        "tag": tag,
        }
    )

def ask(request):
    return render(request, "ask.html")

def question(request, question_id):
    return render(request, "question.html", {
        "question": QUESTIONS[int(question_id)],
        "answers": paginate(QUESTIONS[int(question_id)].get("answers"), request, per_page=30),
        }
    )

def login(request):
    return render(request, "login.html")

def signup(request):
    return render(request, "signup.html")

def paginate(obj_list, request, per_page=10):
    page_num = request.GET.get("page", 1)
    paginator = Paginator(obj_list, per_page)
    try:
        page_num = int(page_num)
    except:
        page_obj = paginator.page(1)
        return page_obj
    if page_num > 0:
        page_obj = paginator.page(page_num)
    else:
        page_obj = paginator.page(1)
    return page_obj