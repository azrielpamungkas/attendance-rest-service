import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim
from utils.gps import validation, detecor
from apps.classrooms.models import ClassroomTimetable, ClassroomAttendance
from students import serializers


def current_lecture(user_id):
    try:
        current_lecture = ClassroomTimetable.objects.all(

        ).filter(date=datetime.date.today()
                 ).filter(start_time__lte=datetime.datetime.now(
                 ).time()).filter(
            end_time__gt=datetime.datetime.now().time()
        ).filter(subject__classroom__student=user_id).first()
        return current_lecture
    except:
        return None


class StudentDashboard(APIView):
    """
    path: /student/
    """
    authentication_classes = [
        authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        now = datetime.datetime.now().time()

        if now < datetime.time(12, 00, 0):
            greeting = "Selamat Pagi"
        elif now < datetime.time(15, 00, 0):
            greeting = "Selamat Siang"
        elif now < datetime.time(18, 00, 0):
            greeting = "Selamat Sore"
        else:
            greeting = "Selamat Malam"

        user = User.objects.get(id=request.user.id)
        name = "{} {}".format(user.first_name, user.last_name)
        data = {'status_code': '000',
                'data': {'greet': greeting,
                         }}
        try:
            lecture = current_lecture(request.user.id)
            data['data']['current_lecture'] = {
                'subject': lecture.subject.name,
                'teacher': "{} {}".format(
                    lecture.subject.teacher.first_name,
                    lecture.subject.teacher.last_name),
                'time': "{} - {} WIB".format(
                    lecture.start_time.strftime("%H:%M"),
                    lecture.end_time.strftime("%H:%M")),
            }
            return Response(data)
        except:
            return Response(data)


class StudentPresenceList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lectures = ClassroomTimetable.objects.all().filter(date=datetime.date.today())
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
        timetables = ClassroomTimetable.objects.all()
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
    """
    path : /student/history/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        history = ClassroomAttendance.objects.all().filter(student=request.user.id)
        data = {
            'data': {

            }
        }
        num = 0
        for h in history:
            num += 1
            data['data'][num] = {
                'name': h.student.username,
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
        total = ClassroomTimetable.objects.all().filter(
            subject__classroom__student=self.request.user.id).filter(
                date__lte=datetime.datetime.now().date()).count()
        hadir = ClassroomAttendance.objects.all().filter(student=request.user.id
                                                         ).filter(status="HADIR").filter(
            timetable__date__lte=datetime.datetime.now().date()).count() / total

        ijin = ClassroomAttendance.objects.all().filter(
            student=request.user.id
        ).filter(status="IJIN").count() / total

        sakit = ClassroomAttendance.objects.all().filter(
            student=request.user.id
        ).filter(status="SAKIT").filter(
            timetable__date__lte=datetime.datetime.now().date()).count() / total

        alpha = ClassroomAttendance.objects.all().filter(
            student=request.user.id
        ).filter(status="ALPHA").filter(
            timetable__date__lte=datetime.datetime.now().date()).count() / total
        return Response({'status_code': 16, 'message': 'Success', 'data': {
            'hadir': hadir,
            'ijin': ijin,
            'sakit': sakit,
            'alpha': alpha,
            'kehadiran': 1.0 - (ijin+sakit+alpha)/total
        }})


class StudentSubmitAttendance(APIView):
    """
    path: student/submit/

    """
    serializer_class = serializers.SubmitAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lat = self.request.query_params.get('lat'),
        lng = self.request.query_params.get('lng')
        location = detecor(lat=lat, lng=lng)
        data = current_lecture(request.user.id)
        if data:
            detail_lecture = {
                'name': data.subject.name,
                'address': location,
                'teacher': "{} {}".format(
                    data.subject.teacher.first_name,
                    data.subject.teacher.last_name),
                'date': data.date,
                'token': data.token,
                'time': "{} - {} WIB".format
                (data.start_time.strftime("%H:%M"),
                 data.end_time.strftime("%H:%M")),
            }

            if ClassroomAttendance.objects.filter(student_id=request.user.id, id=data.id):
                return Response({
                    'status_code': 14,
                    'message': 'Anda sudah absen',
                    'data': detail_lecture
                })
            return Response({
                'status_code': 11,
                'message': 'ada kelas',
                'data': detail_lecture,
            })
        return Response({
            'status_code': 16,
            'address': location,
            'message': 'tidak ada kelas saat ini',
        })

    def post(self, request):
        lecture = current_lecture(user_id=request.user.id)
        if lecture:
            submit_data = request.data.copy()
            submit_data['student'] = request.user.id
            submit_data['timetable'] = lecture.id
            # Check Token
            if submit_data.pop('token', 0)[0] == lecture.token:
                # Check Coordinate
                if validation(lat=submit_data.pop('lat', 0).pop(),
                              lng=submit_data.pop('lng', 0).pop()):
                    serializer = serializers.SubmitAttendanceSerializer(
                        data=submit_data)
                    if serializer.is_valid():
                        student = ClassroomAttendance.objects.get(student=request.user.id,
                                                                  timetable=submit_data['timetable']
                                                                  )

                        if student and student.status == "ALPHA":
                            student.status = submit_data['status']
                            student.save()
                            return Response(
                                {'status_code': 15,
                                    'message': 'Anda Berhasil Absen',
                                 })
                        return Response({'status_code': 14,
                                         'message': 'Anda sudah absen'})
                    return Response({'status_code': 911,
                                    'data': serializer.errors})
                return Response({'status_code': 15,
                                 'message': 'anda di luar titik poinnt'})
            # Error Token
            return Response({"status_code": 12, "message": "Token anda salah"})
