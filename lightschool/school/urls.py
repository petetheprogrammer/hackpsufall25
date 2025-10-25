from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    path('', views.home, name='home'),
    path('set-lang/', views.set_lang, name='set_lang'),
    path('subject/<str:subject>/grade/<int:grade>/', views.subject_grade, name='subject_grade'),
    path('lesson/<str:subject>/<int:grade>/<str:unit_id>/', views.lesson, name='lesson'),
    path('quiz/<str:subject>/<int:grade>/<str:unit_id>/', views.quiz, name='quiz'),
    path('api/lessons/', views.api_lessons, name='api_lessons'),
    path('api/progress/set/', views.api_progress_set, name='api_progress_set'),
    path('api/progress/get/', views.api_progress_get, name='api_progress_get'),
    path('api/tutor/', views.api_tutor, name='api_tutor'),
]