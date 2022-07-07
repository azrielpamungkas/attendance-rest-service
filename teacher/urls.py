from django.urls import path
from . import views


urlpatterns = [
    path("v1/teacher/", views.TeacherDashboard.as_view()),
    path("v1/teacher/class/", views.DetailPresence.as_view()),
    path("v1/teacher/info/", views.DetailPresence.as_view()),
]
