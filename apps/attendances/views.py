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
            'clock_in': "__:__",
            'clock_out': "__:__",
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
                    if obj.clock_in and obj.clock_out != None:
                        response['clock_in'] = f"{obj.clock_in.hour}:{obj.clock_in.minute} WIB"
                        response['clock_out'] = f"{obj.clock_out.hour}:{obj.clock_out.minute} WIB"
                        response['attendance_type'] = 'done'
                    elif obj.clock_in != None and obj.clock_out == None:
                        response['clock_in'] = f"{obj.clock_in.hour}:{obj.clock_in.minute} WIB"
                        response['attendance_type'] = 'Clock-Out'
                except:
                    response['clock_in'] = '__:__'
                    response['clock_out'] = '__:__'
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
            attendance = AttendanceTimetable.objects.all().filter(
                date=datetime.date.today()).filter(role="MRD").first()
            try:
                obj = Attendance.objects.get(
                    user=request.user.id, timetable=attendance.id)
                if obj.clock_in != None and obj.clock_out == None:
                    obj.clock_out = time
                    response = {'status': 200,
                                'attendance_type': 'done',
                                'message': 'anda berhasil clock out',
                                'clock_in': f"{obj.clock_in.hour}:{obj.clock_in.minute} WIB",
                                'clock_out': f"{obj.clock_out.hour}:{obj.clock_out.minute} WIB"}
                    obj.save()
                    return Response(response)
                return Response({
                    'error': 'invalid_post',
                    'error_description': 'Anda sudah absen untuk saat ini'
                })
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
                response = {'status': 200,
                            'attendance_type': 'Clock-Out',
                            'message': 'Anda berhasil clock in',
                            'clock_in': f"{obj.clock_in.hour}:{obj.clock_in.minute} WIB",
                            'clock_out': '__:__'}
                obj.save()
                return Response(response)
