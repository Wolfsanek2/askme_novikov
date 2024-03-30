from django.urls import path

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('settings/', views.settings, name='settings'),
    path('', views.index, name='logout'),
    path('tag/<tag>', views.tag, name='tag'),
    path('ask/', views.ask, name='ask'),
    path('question/<question_id>', views.question, name='question'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
]