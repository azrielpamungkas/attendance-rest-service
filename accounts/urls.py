from django.urls import path
from .views import auth_token


urlpatterns = [
    path("v1/obtain-token/", auth_token),
]
