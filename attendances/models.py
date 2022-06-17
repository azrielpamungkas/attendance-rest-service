from django.db import models
from classrooms.models import Subject
from timetables.models import Timetable
from django.contrib.auth.models import User

# Create your models here.
STATUS = (
    ('ALPHA', 'alpha'),
    ('HADIR', 'hadir'),
    ('IJIN', 'ijin'),
)


class StudentAttendance(models.Model):
    name = models.CharField(max_length=200, null=True, editable=False)
    status = models.CharField(
        default="ALPHA", choices=STATUS, max_length=20, null=True, editable=False)
    timetable = models.ForeignKey(
        Timetable, on_delete=models.CASCADE, null=True)
    token = models.CharField(max_length=4, blank=True)

    def __str__(self) -> str:
        return "{} {}".format(self.name, self.status)

    def save(self):
        pass