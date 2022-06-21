from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
User = get_user_model()


class Classroom(models.Model):
    grade = models.CharField(max_length=40)
    homeroom_teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wali_kelas")
    student = models.ManyToManyField(User, related_name="kelasku")

    def __str__(self):
        return self.grade

    class Meta:
        verbose_name_plural = "Kelas"


class ClassroomSubject(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=15)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pengajar')
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name="subjects")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Mata Pelajaran"


STATUS = (
    ('ALPHA', 'alpha'),
    ('HADIR', 'hadir'),
    ('IJIN', 'ijin'),
)


class ClassroomTimetable(models.Model):
    token = models.CharField(max_length=4, blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)
    subject = models.ForeignKey(
        ClassroomSubject, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        self.token = get_random_string(length=4).upper()
        super(ClassroomTimetable, self).save(*args, **kwargs)
        for student in self.subject.classroom.student.all():
            print(student)
            ClassroomAttendance.objects.create(
                student=self.student.id,
                status="ALPHA",
                timetable=self)
            ClassroomAttendance.save(self, *args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.token, self.subject.name)

    class Meta:
        verbose_name_plural = "Jadwal Kelas"


class ClassroomAttendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        default="ALPHA", choices=STATUS, max_length=20, null=True, editable=True)
    timetable = models.ForeignKey(ClassroomTimetable,
                                  on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return "{} {}".format(self.student.username, self.status)

    class Meta:
        verbose_name_plural = "Kehadiran Kelas"
