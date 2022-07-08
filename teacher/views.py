import datetime
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.classrooms.models import (
    ClassroomAttendance,
    ClassroomSubject,
    ClassroomTimetable,
)
from apps.attendances.models import AttendanceTimetable, Attendance
from utils.gps import detector
from utils.shortcuts import current_lecture_teacher


class TeacherInfo(APIView):
    def get(self, request):
        res = {
            "classrooms": [],
            "user": {
                "first_name": "Azriel",
                "last_name": "Sebastian",
                "username": "124124",
            },
        }
        obj = ClassroomSubject.objects.filter(teacher=request.user.id)
        if obj:
            for sub in obj:
                res["classrooms"].append(
                    {
                        "subject": sub.name,
                        "grade": sub.classroom.grade,
                    }
                )
            return Response(res)
        return Response(res)


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
                "work_time": (lambda x: None if x is None else x.work_time)(
                    attendace_obj
                ),
                "home_time": (lambda x: None if x is None else x.home_time)(
                    attendace_obj
                ),
                "user": {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "address": detector(geo=self.request.query_params.get("geo")),
                },
                "recent_activity": [],
                "status_button": {
                    "clockIn": False,
                    "clockOut": False,
                },
                "message": "",
            }
            if attendace_obj != None:
                res["status_button"]["clock_in"] = True
            if user_attendance != None:
                if (
                    user_attendance.clock_in != None
                    and user_attendance.clock_out == None
                ):
                    res["status_button"]["clock_out"] = True
                elif (
                    user_attendance.obj.clock_time != None
                    and user_attendance.obj.clok_out != None
                ):
                    res["status_button"]["clock_in"] = False
                    res["status_button"]["clock_out"] = False

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

    def post(self, request):
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
                "work_time": (lambda x: None if x is None else x.work_time)(
                    attendace_obj
                ),
                "home_time": (lambda x: None if x is None else x.home_time)(
                    attendace_obj
                ),
                "user": {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "address": detector(geo=self.request.query_params.get("geo")),
                },
                "recent_activity": [],
                "status_button": {
                    "clock_in": False,
                    "clock_out": False,
                },
                "message": "",
            }
            if attendace_obj != None:
                res["status_button"]["clock_in"] = True
            if attendace_obj != None:
                if attendace_obj.clock_time != None and attendace_obj.clock_out == None:
                    res["status_button"]["clock_out"] = True
                    res["message"] = "Anda berhasil clock-in"
                elif (
                    attendace_obj.obj.clock_time != None
                    and attendace_obj.obj.clok_out != None
                ):
                    res["status_button"]["clock_in"] = False
                    res["status_button"]["clock_out"] = False
                    res["message"] = "Anda berhasil clock-out"

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


class TeacherSchedule(APIView):
    def get(self, request):
        clasroom_timetable_qry = ClassroomTimetable.objects.filter(
            subject__teacher=request.user.id
        )
        res = {}
        for obj in clasroom_timetable_qry:
            res.setdefault(obj.date.strftime("%-m/%-d/%Y"), [])
            res[obj.date.strftime("%-m/%-d/%Y")].append(
                {
                    "id": obj.id,
                    "on_going": (
                        lambda x, y: False
                        if y == None
                        else (True if x == y.id else False)
                    )(
                        obj.id,
                        current_lecture_teacher(request.user.id, ClassroomTimetable),
                    ),
                    "subject": obj.subject.name,
                    "classroom": obj.subject.classroom.grade,
                    "teacher": {
                        "first_name": obj.subject.teacher.first_name,
                        "last_name": obj.subject.teacher.last_name,
                    },
                    "start_time": obj.start_time,
                    "end_time": obj.end_time,
                }
            )
        return Response(res)


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
