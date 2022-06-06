from unicodedata import name
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class Classroom(models.Model):
    grade = models.CharField(max_length=40)
    homeroom_teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wali_kelas")
    student = models.ManyToManyField(User, related_name="kelasku")

    def __str__(self):
        return self.grade


class Subject(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=15)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pengajar')
    classroom = models.ManyToManyField(Classroom, related_name="subjects")

    def __str__(self):
        return self.name
