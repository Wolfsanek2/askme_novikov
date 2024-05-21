from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from app.models import *
from app import models, forms
from random import randint

ANSWERS_PER_PAGE = 30
QUESTIONS_PER_PAGE = 20

# Create your views here.

def index(request):
    questions = models.Question.objects.get_new()
    question_list = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    profile = models.Profile.objects.get_by_user_id(request.user.id)
    context = {
        "questions": question_list,
        "profile": profile,
    }
    return render(request, "index.html", context)

def hot_questions(request):
    questions = models.Question.objects.get_hot()
    question_list = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    profile = models.Profile.objects.filter(user__id=request.user.id).first()
    context = {
        "questions": question_list,
        "profile": profile,
    }
    return render(request, "hot_questions.html", context)

@csrf_protect
@login_required(login_url="login", redirect_field_name="continue")
def settings(request):
    user_id = request.user.id
    profile = models.Profile.objects.filter(user__id=user_id).first()
    if request.method == "POST":
        settings_form = forms.SettingsForm(data=request.POST, files=request.FILES, user_id=user_id)
        if settings_form.is_valid():
            settings_form.save()
            request.user = profile.user
            return redirect("settings")
    else:
        try:
            data = {
                "username": profile.user.username,
                "email": profile.user.email,
                "first_name": profile.user.first_name,
            }
            files = {
                "avatar": profile.avatar,
            }
        except:
            data = {}
            files = {}
        settings_form = forms.SettingsForm(data=data, files=files, user_id=user_id)
    context = {
        "form": settings_form,
        "profile": profile,
    }
    return render(request, "settings.html", context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get("continue", reverse("index")))

def tag(request, tag_name):
    try:
        Tag.objects.get(name = tag_name)
    except:
        return HttpResponseNotFound("page not found")
    questions = Question.objects.get_by_tag(tag_name)
    questions_list = paginate(questions, request, per_page=20)
    profile = models.Profile.objects.filter(user__id=request.user.id).first()
    context = {
        "questions": questions_list,
        "tag": tag_name,
        "profile": profile,
    }
    return render(request, "tag.html", context)

@csrf_protect
@login_required(login_url="login", redirect_field_name="continue")
def ask(request):
    if request.method == "POST":
        question_form = forms.QuestionForm(data=request.POST)
        print(question_form.data)
        if question_form.is_valid():
            question = question_form.save(request.user.id)
            return redirect(f"question", question_id=question.id)
    else:
        question_form = forms.QuestionForm()
    profile = models.Profile.objects.filter(user__id=request.user.id).first()
    context = {
        "form": question_form,
        "profile": profile,
    }
    return render(request, "ask.html", context)

@csrf_protect
def question(request, question_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            answer_form = forms.AnswerForm(data=request.POST)
            if answer_form.is_valid():
                answer = answer_form.save(request.user.id, question_id)
                answer_form = forms.AnswerForm()
                answers = Answer.objects.get_best_for_question(question_id)
                page_num = get_page_num(answers, answer.id)
                url = reverse("question", kwargs={"question_id": question_id}) + f"?page={page_num}" + f"#{answer.id}"
                return redirect(url)
        else:
            return redirect("login")
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponseNotFound("page not found")
    answer_form = forms.AnswerForm()
    answers = Answer.objects.get_best_for_question(question_id)
    answers_list = paginate(answers, request, per_page=ANSWERS_PER_PAGE)
    user_id = request.user.id
    profile = models.Profile.objects.filter(user__id=user_id).first()
    context = {
        "question": question,
        "answers": answers_list,
        "form": answer_form,
        "profile": profile,
    }
    return render(request, "question.html", context)

@csrf_protect
def login(request):
    if request.method == "POST":
        login_form = forms.LoginForm(data=request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(request.GET.get("continue", reverse("index")))
            else:
                login_form.add_error(None, "Wrong login or password")
    else:
        login_form = forms.LoginForm()
    context = {
        "form": login_form,
    }
    return render(request, "login.html", context)

@csrf_protect
def signup(request):
    if request.method == "POST":
        print(request.FILES)
        signup_form = forms.SignupForm(data=request.POST, files=request.FILES)
        if signup_form.is_valid():
            profile = signup_form.save()
            if profile:
                auth.login(request, profile.user)
                return redirect(reverse("index"))
    else:
        signup_form = forms.SignupForm()
    context = {
        "form": signup_form,
    }
    return render(request, "signup.html", context)

def paginate(query_set, request, per_page=10):
    page_num = request.GET.get("page", "1")
    paginator = Paginator(query_set, per_page)
    try:
        page_obj = paginator.page(page_num)
    except:
        page_obj = paginator.page(1)
    return page_obj

def get_page_num(answers, answer_id, per_page=ANSWERS_PER_PAGE):
    answers_list = answers.all()
    for i in range(len(answers_list)):
        if (answers_list[i].id == answer_id):
            page_num = int(i / ANSWERS_PER_PAGE) + 1
            break
    return page_num