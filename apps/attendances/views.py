from rest_framework.views import APIView
from . import serializers
from utils.gps import detector
from .models import Attendance, AttendanceTimetable
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
import datetime
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
# Bikin serializer untuk ini agar bisa detect geo nantinya

from .docs import AttendanceDoc

doc = AttendanceDoc()


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
        if request.user.groups.filter(name="student").exists():
            attendance = (
                AttendanceTimetable.objects.all()
                .filter(date=datetime.date.today())
                .filter(role="MRD")
                .first()
            )
            obj = Attendance.objects.filter(
                user=request.user.id, timetable=attendance.id
            ).first()
            if obj:
                if obj.clock_in != None and obj.clock_out == None:
                    if time >= attendance.home_time:
                        obj.clock_out = time
                        obj.save()
                        response = {
                            "status": 200,
                            "clock_out": f"{time.hour}:{time.minute}",
                            "next_attendance_status": "Done!",
                            "message": "anda berhasil clock out",
                        }
                        return Response(response)
                    return Response(
                        {
                            "error": {
                                "status": "invalid_clock_out",
                                "message": "Anda belum bisa clock out untuk saat ini",
                            }
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
                    status=(lambda x: "H" if x <= attendance.work_time else "T"),
                )
                response = {
                    "status": 200,
                    "clock_in": f"{time.hour}:{time.minute}",
                    "next_attendance_status": "Clock-Out",
                    "message": "Anda berhasil clock in",
                }
                return Response(response)
        return PermissionDenied
