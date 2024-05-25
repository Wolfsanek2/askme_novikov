from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout, name='logout'),
    path('tag/<tag_name>', views.tag, name='tag'),
    path('ask/', views.ask, name='ask'),
    path('question/<question_id>', views.question, name='question'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('question/<question_id>/like', views.question_like, name='question_like'),
    path('question/<question_id>/dislike', views.question_dislike, name='question_dislike'),
    path('answer/<answer_id>/like', views.answer_like, name='answer_like'),
    path('answer/<answer_id>/dislike', views.answer_dislike, name='answer_dislike'),
    path('answer/<answer_id>/is_correct', views.answer_is_correct, name = 'answer_is_correct'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)