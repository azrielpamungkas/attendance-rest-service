from django.urls import path
from . import views

urlpatterns = [
    path('', views.AttendanceView.as_view())
]
