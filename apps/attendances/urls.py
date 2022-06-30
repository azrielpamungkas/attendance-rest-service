from django.urls import path
from . import views

urlpatterns = [path("v1/attendance/", views.AttendanceView.as_view())]
