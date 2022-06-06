from time import time
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from classrooms.models import Subject
from timetables.models import Timetable
from attendances.models import StudentAttendance
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from geopy import distance
from . import serializers
import datetime
import random


def c_lecture(user):
    try:
        current_lecture = Timetable.objects.get(date=datetime.date.today(
        ), start_time__lte=datetime.datetime.now().time(), end_time__gt=datetime.datetime.now().time(),
            subject__classroom__student=user)
        return current_lecture
    except ObjectDoesNotExist:
        return None


class SubmitAttendance(APIView):
    serializer_class = serializers.SubmitAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if c_lecture(request.user.id):
            data = c_lecture(request.user.id)
            if StudentAttendance.objects.filter(
                    name="{} {}".format(
                        request.user.first_name, request.user.last_name),
                    timetable=data.id):
                return Response({'status_code': 14, 'message': 'Anda sudah absen', 'data': {'name': data.subject.name, 'teacher': "{} {}".format(data.subject.teacher.first_name, data.subject.teacher.last_name), 'time': "{} - {} WIB".format(data.start_time.strftime("%H:%M"),
                                                                                                                                                                                                                                                data.end_time.strftime("%H:%M"))}})
            return Response({'status_code': 11, 'message': 'ada kelas', 'data': {'name': data.subject.name, 'teacher': "{} {}".format(data.subject.teacher.first_name, data.subject.teacher.last_name),
                                                                                 'date': data.date, 'token': data.token,
                             'time': "{} - {} WIB".format(data.start_time.strftime("%H:%M"),
                                                          data.end_time.strftime("%H:%M"))},
                             })

        return Response({'message': 'tidak ada kelas saat ini', 'data': {}})

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        if c_lecture(request.user.id):
            submit_data = request.data.copy()
            submit_data['name'] = "{} {}".format(
                request.user.first_name, request.user.last_name)
            try:
                submit_data['timetable'] = c_lecture(request.user.id).id
            except:
                return Response('tidak ada kelas')

            center_point = [
                {'lat': -6.990244896200767, 'lng': 110.42050151945978}]
            # center_point = [{'lat': -7.9120362, 'lng': 110.3428084}]
            test_point = [
                {'lat': submit_data['lat'], 'lng': submit_data['lng']}]
            radius = 0.06  # in kilometer
            center_point_tuple = tuple(center_point[0].values())
            test_point_tuple = tuple(test_point[0].values())
            try:
                dis = distance.great_circle(
                    center_point_tuple, test_point_tuple).km
            except ValueError:
                return Response({'message': 'Lokasi anda tidak valid', 'data': {}})

            # if submit_data['token'] == c_lecture(request.user.id).token:
            if submit_data['token'] == 'TEST':
                # if dis <= radius:
                if True:
                    del submit_data['lat']
                    del submit_data['lng']
                    serializer = serializers.SubmitAttendanceSerializer(
                        data=submit_data)
                    if serializer.is_valid():
                        if not StudentAttendance.objects.filter(name=submit_data['name'], timetable=submit_data['timetable']).exists():
                            serializer.save(
                                name=submit_data['name'], timetable=Timetable.objects.get(id=submit_data['timetable']))
                            return Response({'status_code': 15, 'message': 'Anda Berhasil Absen', 'data': serializer.data})
                        return Response({'status_code': 14, 'message': "absen", 'data': {}})
                    else:
                        return Response({'data': serializer.errors})
                return Response({'status_code': 13, 'message': 'Anda diluar titik point'})
            return Response({"status_code": 12, "message": "Token anda salah"})
        return Response('Tidak Ada Kelas Saat Ini')


class StudentDashboard(APIView):
    authentication_classes = [
        authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        if datetime.datetime.now().time() < datetime.time(12, 00, 0):
            greeting = "Selamat Pagi"
        elif datetime.datetime.now().time() < datetime.time(15, 00, 0):
            greeting = "Selamat Siang"
        elif datetime.datetime.now().time() < datetime.time(18, 00, 0):
            greeting = "Selamat Sore"
        else:
            greeting = "Selamat Malam"
        quote = random.choice([
            'Jangan bermain-main dengan perasaan orang lain. Jangan, itu menyakitkan. Dan besok lusa, boleh jadi giliran perasaan kita yang dijadikan mainan orang lain.',
            'Kalau kita menyelamatkan hati orang lain, suatu saat Tuhan pasti akan menyelamatkan kita.',
            'Hidupmu hanya kamu yang menjalani. Jadi, apa pun keputusan yang kamu ambil harus kamu jalankan dengan sepenuh hati.',
            'Bukan tempatnya yang sempit, hatinya saja yang kurang lapang. Bukan rezekinya yang sedikit, bersyukurnya saja yang kurang.',
            'Cinta tak selamanya indah, tetapi tergantung siapa yang menjalaninya',
            'Tidak perlu kata-kata yang penting bukti nyata'
            'Masa lalumu milikmu, masa laluku milikku',
        ])
        user = User.objects.get(id=request.user.id)
        name = "{} {}".format(user.first_name, user.last_name)
        data = {'status_code': '000',
                'message': 'success',
                'data': {'greet': greeting,
                         'quote': quote,
                         'name': name,
                         }}
        try:
            current_lecture = c_lecture(request.user.id)

            data['data']['current_lecture'] = {
                'subject': current_lecture.subject.name,
                'teacher': "{} {}".format(current_lecture.subject.teacher.first_name,
                                          current_lecture.subject.teacher.last_name),
                'time': "{} - {} WIB".format(current_lecture.start_time.strftime("%H:%M"), current_lecture.end_time.strftime("%H:%M")),
            }
            return Response(data)
        except:
            data['data']['current_lecture'] = {}
            return Response(data)


class StudentPresenceList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lectures = Timetable.objects.all().filter(date=datetime.date.today())
        data = {
            'status_code': '000',
            'message': "success",
            'data': {'lectures': {}}
        }

        num = 0
        for lecture in lectures:
            num += 1
            data['data']['lectures'][num] = {
                'name': lecture.subject.name,
                'start': lecture.start_time.strftime("%H:%M"),
                'end': lecture.end_time.strftime("%H:%M"),
                'teacher': "{} {}".format(lecture.subject.teacher.first_name, lecture.subject.teacher.last_name),

            }

        return Response(data)


class StudentTimetables(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        timetables = Timetable.objects.all()
        data = {'status_code': '000',
                'message': "success", 'data': {

                }}
        num = 0
        for timetable in timetables:
            num += 1
            data['data'][num] = {
                'name': timetable.subject.name,
                'teacher': "{} {}".format(timetable.subject.teacher.first_name,  timetable.subject.teacher.last_name),
                'date': timetable.date,
                'start': timetable.start_time.strftime("%H:%M"),
                'end': timetable.end_time.strftime("%H:%M"),
            }

        return Response(data)


class StudentHistory(APIView):
    #authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        name = "{} {}".format(request.user.first_name, request.user.last_name)
        history = StudentAttendance.objects.all().filter(name=name)
        data = {
            'data': {

            }
        }
        num = 0
        for h in history:
            num += 1
            data['data'][num] = {
                'name': h.name,
                'status': h.status,
                'subject': h.timetable.subject.name,
                'date': h.timetable.date.strftime("%A %-d %B %Y"),
                'time': "{} - {} WIB".format(h.timetable.start_time.strftime("%H:%M"),
                                             h.timetable.end_time.strftime("%H:%M")),
            }
        return Response(data)


class StudentStatistic(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total = Timetable.objects.all().filter(
            subject__classroom__student=self.request.user.id).count()
        hadir = StudentAttendance.objects.all().filter(
            name="{} {}".format(self.request.user.first_name,
                                self.request.user.last_name)
        ).filter(status="HADIR").count()
        ijin = StudentAttendance.objects.all().filter(
            name="{} {}".format(self.request.user.first_name,
                                self.request.user.last_name)
        ).filter(status="IJIN").count()
        sakit = StudentAttendance.objects.all().filter(
            name="{} {}".format(self.request.user.first_name,
                                self.request.user.last_name)
        ).filter(status="SAKIT").count()
        alpha = StudentAttendance.objects.all().filter(
            name="{} {}".format(self.request.user.first_name,
                                self.request.user.last_name)
        ).filter(status="ALPHA").count()

        return Response({'status_code': 16, 'message': 'Success', 'data': {
            'hadir': hadir/total,
            'ijin': ijin / total,
            'sakit': sakit/total,
            'alpha': alpha/total,
            'kehadiran': 1.0 - (ijin+sakit+alpha)/total
        }})
