from datetime import date
from django.db import models


class AttendanceTimetable(models.Model):
    class RoleInSchool(models.TextChoices):
        STUDENT = 'MRD', 'Student'
        STAFF = 'KWN', 'Staff'
        TEACHER = 'GRU', 'Teacher'
        STUDENT_HOME = 'MRD_HOME', 'Student Home'
        STAFF_HOME = 'KWN_HOME', 'Staff Home'
        TEACHER_HOME = 'GRU_HOME', 'Teacher Home'

    date = models.DateField()
    work_time = models.TimeField()
    home_time = models.TimeField()
    role = models.CharField(choices=RoleInSchool.choices, max_length=20)

    def __str__(self):
        return f"({self.role}) - {self.date.strftime('%b %d, %Y')}"

    class Meta:
        verbose_name_plural = "Penjadwalan Umum"


class Attendance(models.Model):
    clock_in = models.TimeField()
    clock_out = models.TimeField()
    status = models.CharField(max_length=20)
    timetable = models.ForeignKey(
        AttendanceTimetable, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Daftar Hadir"
