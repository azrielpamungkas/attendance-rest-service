from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from apps.classrooms.models import ClassroomTimetable
from . import serializers
from utils.gps import detector
from .models import Attendance, AttendanceTimetable, Leave
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
import datetime
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema

from .docs import AttendanceDoc

doc = AttendanceDoc()


class LeaveView(CreateAPIView):
    queryset = ""

    def get(self, request):
        today = datetime.datetime.today().date()
        classroom_timetable_q = ClassroomTimetable.objects.filter(
            date__range=(today, today + datetime.timedelta(days=10))
        )
        print(classroom_timetable_q)
        attendance_timetable_q = AttendanceTimetable.objects.filter(
            date__range=(today, today + datetime.timedelta(days=10))
        )
        res = {
            "history": {},
            "attendanceTimetable": [
                {"id": data.id, "name": data.__str__()}
                for data in attendance_timetable_q
            ],
            "classroomTimetable": [
                {"id": data.id, "name": data.__str__()}
                for data in classroom_timetable_q
            ],
        }

        queryset = Leave.objects.filter(user=request.user.id)
        print(queryset)
        for q in queryset:
            month_year = "{} {}".format(q.created_at.strftime("%b"), q.created_at.year)
            print(month_year)
            res["history"].setdefault(month_year, [])
            res["history"][month_year].append(
                {
                    "type": (lambda x: "Sakit" if x else "Ijin")(q.leave_type),
                    "mode": (lambda x: "Full Day" if x else "Half Day")(q.leave_mode),
                    "reason": q.reason,
                    "status": (lambda x: "Approved" if x else "Sedang Menunggu")(
                        q.approve
                    ),
                    "status_code": (lambda x: 1 if x else 0)(q.approve),
                    "date": q.created_at.strftime("%d %B %Y"),
                }
            )
        return Response(res)

    def post(self, request, *args, **kwargs):
        print("request post: ", request.data)
        return super().post(request, *args, **kwargs)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.GET.get("type") == "half":
            return serializers.LeaveHalfSer
        else:
            return serializers.LeaveFullSer

    def perform_create(self, serializer):
        if self.request.GET.get("type") == "half":
            leave_mode = 0
        else:
            leave_mode = 1
        serializer.save(user=self.request.user, leave_mode=leave_mode)


class AttendanceView(APIView):
    @swagger_auto_schema(responses=doc.attendance_get)
    def get(self, request):
        geo = self.request.query_params.get("geo")
        if request.user.groups.filter(name="student").exists():
            attendance = (
                AttendanceTimetable.objects.all()
                .filter(date=datetime.date.today())
                .filter(role="MRD")
                .first()
            )
            if attendance:
                obj = (
                    Attendance.objects.filter(timetable__date=datetime.date.today())
                    .filter(user=request.user.id)
                    .first()
                )
                response = {
                    "attendance_type": attendance.role,
                    "attendance_status": (
                        lambda x: None
                        if attendance is None
                        else (
                            "Clock-In"
                            if x is None
                            else (
                                "Clock-Out"
                                if x.clock_in != None and x.clock_out == None
                                else "Done!"
                            )
                        )
                    )(obj),
                    "date": attendance.date,
                    "work_time": attendance.work_time,
                    "home_time": attendance.home_time,
                    "clock_in": (
                        lambda x: None
                        if x is None
                        else (
                            None
                            if x.clock_in is None
                            else f"{x.clock_in.hour}:{x.clock_in.minute}"
                        )
                    )(obj),
                    "clock_out": (
                        lambda x: None
                        if x is None
                        else (
                            None
                            if x.clock_out is None
                            else f"{x.clock_out.hour}:{x.clock_out.minute}"
                        )
                    )(obj),
                    "user": {"address": detector(geo=geo)},
                }
                return Response(response)
            return Response(
                {
                    "message": {
                        "status": "info",
                        "detail": "tidak ada jadwal untuk hari ini",
                    }
                }
            )
        return PermissionDenied

    @swagger_auto_schema(responses=doc.attendance_post)
    def post(self, request):
        time = datetime.datetime.now().time()
        if True:
            if request.user.groups.filter(name="student").exists():
                attendance = (
                    AttendanceTimetable.objects.all()
                    .filter(date=datetime.date.today())
                    .filter(role="MRD")
                    .first()
                )
            else:
                attendance = (
                    AttendanceTimetable.objects.all()
                    .filter(date=datetime.date.today())
                    .filter(role="GRU")
                    .first()
                )
            obj = Attendance.objects.filter(
                user=request.user.id, timetable=attendance.id
            ).first()
            if obj:
                if obj.clock_in != None and obj.clock_out == None:
                    if attendance.home_time >= time:
                        obj.clock_out = time
                        obj.save()
                        response = {
                            "status": 200,
                            "clock_out": f"{time.hour}:{time.minute}",
                            "next_attendance_status": "Done!",
                            "message": "Anda berhasil clock out",
                        }
                        return Response(response)
                    return Response(
                        {
                            "error": "invalid_clock_out",
                            "message": "Anda belum bisa clock out untuk saat ini",
                        }
                    )
                return Response(
                    {
                        "error": "invalid_post",
                        "error_description": "Anda sudah absen untuk saat ini",
                    }
                )
            else:
                Attendance.objects.create(
                    user=User.objects.get(id=request.user.id),
                    timetable=AttendanceTimetable.objects.get(id=attendance.id),
                    clock_in=time,
                    status=(lambda x: "H" if x <= attendance.work_time else "T")(time),
                )
                response = {
                    "status": 200,
                    "clock_in": f"{time.hour}:{time.minute}",
                    "next_attendance_status": "Clock-Out",
                    "message": "Anda berhasil clock in",
                }
                return Response(response)
        return PermissionDenied
