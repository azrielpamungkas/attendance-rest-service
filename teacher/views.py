import datetime
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.classrooms.models import ClassroomAttendance, ClassroomTimetable
from apps.attendances.models import AttendanceTimetable, Attendance
from utils.gps import detector


class TeacherDashboard(APIView):
    def get(self, request, format=None):
        if request.user.groups.filter(name="teacher").exists():
            attendace_obj = (
                AttendanceTimetable.objects.filter(date=datetime.datetime.today())
                .filter(role="GRU")
                .first()
            )
            user_attendance = Attendance.objects.filter(
                timetable=(lambda x: 192940129401 if x is None else x.id)(attendace_obj)
            ).first()
            if datetime.datetime.now().hour < 12:
                greeting = "Selamat Pagi"
            elif datetime.datetime.now().hour < 15:
                greeting = "Selamat Siang"
            elif datetime.datetime.now().hour < 18:
                greeting = "Selamat Sore"
            else:
                greeting = "Selamat Malam"

            res = {
                "greet": greeting,
                "work_time": (
                    lambda x: None if x is None else f"{x.work_time} - {x.home_time}"
                )(attendace_obj),
                "user": {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "address": detector(geo=self.request.query_params.get("geo")),
                },
                "recent_activity": [],
            }

            for attendance in Attendance.objects.filter(user=request.user.id):
                data = []
                if attendance.clock_in != None:
                    data.append(["clock in", attendance.clock_in])
                    if attendance.clock_out != None:
                        data.append(["clock out", attendance.clock_out])

            if len(data) != 0:
                for d in data:
                    res["recent_activity"].append({"type": d[0], "time": d[1]})
                return Response(res)
            return Response(res)
        raise PermissionDenied


class DetailPresence(APIView):
    def get_student_attendace():
        obj = ClassroomAttendance.objects.get(timetable=id)
        return obj

    def get(self, request):
        obj = (
            ClassroomTimetable.objects.filter(date=datetime.date.today())
            .filter(start_time__lte=datetime.datetime.now().time())
            .filter(end_time__gt=datetime.datetime.now().time())
            .filter(subject__teacher=request.user.id)
            .first()
        )

        if obj:
            res = {
                "name": obj.subject.name,
                "teacher": f"{obj.subject.teacher.first_name}",
                "classroom": obj.subject.classroom.grade,
                "time": f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')} WIB",
                "students": [],
            }
            for student in ClassroomAttendance.objects.filter(timetable=obj.id):
                res["students"].append(
                    {
                        "name": f"{student.student.first_name}",
                        "status": f"{student.status}",
                    }
                )
            return Response(res)
        return Response(
            {
                "name": None,
                "teacher": None,
                "classroom": None,
                "time": None,
                "students": [],
            }
        )
