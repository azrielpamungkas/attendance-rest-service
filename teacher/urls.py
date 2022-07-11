from django.urls import path
from . import views


urlpatterns = [
    path("v1/teacher/", views.TeacherDashboard.as_view()),
    path("v1/teacher/class/", views.teacher_classroom),
    path("v1/teacher/c/", views.teacher_classroom_detail),
    path("v1/teacher/info/", views.teacher_account),
    path("v1/teacher/schedule/", views.TeacherSchedule.as_view()),
]
