from django.urls import path
from students import views


urlpatterns = [
    path('', views.StudentDashboard.as_view()),
    path('presences/', views.StudentPresenceList.as_view()),
    # path('timetables/', views.StudentTimetables.as_view()),
    path('history/', views.StudentHistory.as_view()),
    path('submit/', views.StudentSubmitAttendance.as_view()),
    path('statistic/', views.StudentStatistic.as_view()),
]
