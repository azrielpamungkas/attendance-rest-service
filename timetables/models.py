from django.db import models
from classrooms.models import Subject
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

# Create your models here.


class Timetable(models.Model):
    token = models.CharField(max_length=4, blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        self.token = get_random_string(length=4).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Jadwal"


class StudentAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.first_name
