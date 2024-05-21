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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)