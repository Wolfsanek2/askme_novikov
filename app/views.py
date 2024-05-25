from django.http.response import HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from app.models import *
from app import models, forms
from random import randint
import json

ANSWERS_PER_PAGE = 30
QUESTIONS_PER_PAGE = 20

# Create your views here.

@require_http_methods(["GET"])
def index(request):
    questions = models.Question.objects.get_new()
    question_list = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    profile = models.Profile.objects.get_by_user_id(request.user.id)
    liked_questions, disliked_questions = QuestionsRating.objects.get_liked_disliked_questions(profile)
    context = {
        "questions": question_list,
        "profile": profile,
        "liked_questions": liked_questions,
        "disliked_questions": disliked_questions,
    }
    return render(request, "index.html", context)

@require_http_methods(["GET"])
def hot_questions(request):
    questions = models.Question.objects.get_hot()
    question_list = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    profile = models.Profile.objects.get_by_user_id(request.user.id)
    liked_questions, disliked_questions = QuestionsRating.objects.get_liked_disliked_questions(profile)
    context = {
        "questions": question_list,
        "profile": profile,
        "liked_questions": liked_questions,
        "disliked_questions": disliked_questions,
    }
    return render(request, "hot_questions.html", context)

@csrf_protect
@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(["GET", "POST"])
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

@require_http_methods(["GET"])
def logout(request):
    auth.logout(request)
    return redirect(request.GET.get("continue", reverse("index")))

@require_http_methods(["GET"])
def tag(request, tag_name):
    try:
        Tag.objects.get(name = tag_name)
    except:
        return HttpResponseNotFound("page not found")
    questions = Question.objects.get_by_tag(tag_name)
    questions_list = paginate(questions, request, per_page=20)
    profile = models.Profile.objects.filter(user__id=request.user.id).first()
    liked_questions, disliked_questions = QuestionsRating.objects.get_liked_disliked_questions(profile)
    context = {
        "questions": questions_list,
        "tag": tag_name,
        "profile": profile,
        "liked_questions": liked_questions,
        "disliked_questions": disliked_questions,
    }
    return render(request, "tag.html", context)

@csrf_protect
@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(["GET", "POST"])
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
@require_http_methods(["GET", "POST"])
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
    liked_answers, disliked_answers = AnswersRating.objects.get_liked_disliked_answers(profile)
    question_liked, question_disliked = QuestionsRating.objects.check_liked_disliked_question(profile, question_id)
    context = {
        "question": question,
        "answers": answers_list,
        "form": answer_form,
        "profile": profile,
        "liked_answers": liked_answers,
        "disliked_answers": disliked_answers,
        "question_liked": question_liked,
        "question_disliked": question_disliked,
    }
    return render(request, "question.html", context)

@csrf_protect
@require_http_methods(["GET", "POST"])
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
@require_http_methods(["GET", "POST"])
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

@csrf_protect
@require_http_methods(["POST"])
def question_like(request, question_id):
    body = json.loads(request.body)
    profile = Profile.objects.get(user=request.user)
    question = Question.objects.get(id=question_id)
    QuestionsRating.objects.like(profile, question)
    body["rating"] = question.rating
    return JsonResponse(body)

@csrf_protect
@require_http_methods(["POST"])
def question_dislike(request, question_id):
    body = json.loads(request.body)
    profile = Profile.objects.get(user=request.user)
    question = Question.objects.get(id=question_id)
    QuestionsRating.objects.dislike(profile, question)
    body["rating"] = question.rating
    return JsonResponse(body)

@csrf_protect
@require_http_methods(["POST"])
def answer_like(request, answer_id):
    print(answer_id)
    body = json.loads(request.body)
    profile = Profile.objects.get(user=request.user)
    answer = Answer.objects.get(id=answer_id)
    AnswersRating.objects.like(profile, answer)
    body["rating"] = answer.rating
    return JsonResponse(body)

@csrf_protect
@require_http_methods(["POST"])
def answer_dislike(request, answer_id):
    body = json.loads(request.body)
    profile = Profile.objects.get(user=request.user)
    answer = Answer.objects.get(id=answer_id)
    AnswersRating.objects.dislike(profile, answer)
    body["rating"] = answer.rating
    return JsonResponse(body)

@csrf_protect
@require_http_methods(["POST"])
def answer_is_correct(request, answer_id):
    body = json.loads(request.body)
    question_id = body["questionId"]
    old_answer = Answer.objects.filter(is_correct=True).first()
    if old_answer:
        old_answer.is_correct = False
        old_answer.save()
    is_correct = body["is_correct"]
    answer = Answer.objects.get(id=answer_id)
    answer.is_correct = True if is_correct else False
    answer.save()
    return JsonResponse(body)

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