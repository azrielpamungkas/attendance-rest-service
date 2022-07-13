from django.contrib import admin
from .models import (
    Classroom,
    ClassroomJournal,
    ClassroomSubject,
    ClassroomTimetable,
    ClassroomAttendance,
)

# Register your models here.
admin.site.register(Classroom)
admin.site.register(ClassroomSubject)
admin.site.register(ClassroomTimetable)
admin.site.register(ClassroomAttendance)
admin.site.register(ClassroomJournal)
