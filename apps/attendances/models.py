from django.db import models
from django.contrib.auth.models import User
from apps.classrooms.models import ClassroomSubject, ClassroomTimetable


class AttendanceTimetable(models.Model):
    class RoleInSchool(models.TextChoices):
        STUDENT = "MRD", "Student"
        STAFF = "KWN", "Staff"
        TEACHER = "GRU", "Teacher"
        STUDENT_HOME = "MRD_HOME", "Student Home"
        STAFF_HOME = "KWN_HOME", "Staff Home"
        TEACHER_HOME = "GRU_HOME", "Teacher Home"

    date = models.DateField()
    work_time = models.TimeField()
    home_time = models.TimeField()
    role = models.CharField(choices=RoleInSchool.choices, max_length=20)

    def __str__(self):
        return f"({self.role}) - {self.date.strftime('%b %d, %Y')}"

    class Meta:
        verbose_name_plural = "Penjadwalan Umum"


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20)
    timetable = models.ForeignKey(AttendanceTimetable, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Daftar Hadir"


class Leave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    leave_mode = models.SmallIntegerField()
    leave_type = models.SmallIntegerField()
    attendance_scheduled = models.ManyToManyField(AttendanceTimetable, blank=True)
    classroom_scheduled = models.ManyToManyField(ClassroomTimetable, blank=True)
    reason = models.TextField()
    attachment = models.ImageField(null=True)
    approve = models.BooleanField(null=True, default=None)

    def __str__(self):
        return self.user.username + " " + self.reason
