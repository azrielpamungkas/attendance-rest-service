from rest_framework.views import APIView
from . import serializers
from utils.gps import detecor
from .models import Attendance, AttendanceTimetable
from rest_framework.response import Response
from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.contrib.auth.models import User
# Create your views here.


class AttendanceView(APIView):
    # /v1/attendance?geo={lat},{lng}
    # def current_attendance(role):
    #     try:
    #         current = AttendanceTimetable.objects.all().filter(
    #             date=datetime.date.today()).filter(role=role).first()
    #         return current
    #     except:
    #         return None

    def get(self, request):
        geo = self.request.query_params.get('geo')
        response = {
            'attendance_type': None,
            'date': None,
            'work_time': None,
            'home_time': None,
            'clock_in': None,
            'clock_out': None,
            'user': {
                'address': detecor(geo=geo)
            }
        }
        if request.user.groups.filter(name='student').exists():
            attendance = AttendanceTimetable.objects.all().filter(
                date=datetime.date.today()).filter(role="MRD").first()
            if attendance:
                response['attendance_type'] = attendance.role
                response['date'] = attendance.date
                response['work_time'] = attendance.work_time
                response['home_time'] = attendance.home_time

                try:
                    obj = Attendance.objects.all().filter(
                        user=request.user.id,
                        timetable__date=datetime.date.today()).first()
                    response['clock_in'] = obj.clock_in
                    response['clock_out'] = obj.clock_out
                except:
                    response['clock_in'] = ''
                    response['clock_out'] = ''
                return Response(response)
            return Response({'message': {
                'status': 'info',
                'detail': 'tidak ada jadwal untuk hari ini'
            }})
        return Response({'message': {
            'status': 'warning',
            'detail': 'user belum punya role'
        }})

    def post(self, request):
        time = datetime.datetime.now().time()
        if request.user.groups.filter(name='student').exists():
            attendance = attendance = AttendanceTimetable.objects.all().filter(
                date=datetime.date.today()).filter(role="MRD").first()
            try:
                obj = Attendance.objects.get(user=request.user.id)
                if obj.clock_in != None and obj.clock_out == None:
                    obj.clock_out = time
                    obj.save()
                    return Response("Success")
                return Response("Anda sudah absen untuk saat ini")
            except ObjectDoesNotExist:
                obj = Attendance.objects.create(
                    user=User.objects.get(id=request.user.id),
                    timetable=AttendanceTimetable.objects.get(
                        id=attendance.id),
                    clock_in=time,
                )
                if time <= attendance.work_time:
                    obj.status = 'H'
                else:
                    obj.status = 'T'
                obj.save()
                return Response('sukses')
