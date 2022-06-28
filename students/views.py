import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from utils.gps import validation, detecor
from apps.classrooms.models import ClassroomTimetable, ClassroomAttendance
from students import serializers
from apps.attendances.models import AttendanceTimetable

# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
#             HTTP/1.1 400 Bad Request
# {
#     "error": {
#         "status": 400,
#         "message": "invalid id"
#     }
# }


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


class StudentSubmitAttendance(APIView):
    # path: student/submit/
    serializer_class = serializers.SubmitAttendanceSerializer

    def get(self, request):
        geo = self.request.query_params.get('geo'),
        location = detecor(geo)
        scheduled_obj = current_lecture(request.user.id)
        if scheduled_obj:
            class_time = "{} - {} WIB".format(
                scheduled_obj.start_time.strftime("%H:%M"),
                scheduled_obj.end_time.strftime("%H:%M"))
            teacher_name = "{} {}".format(
                scheduled_obj.subject.teacher.first_name,
                scheduled_obj.subject.teacher.last_name)
            res = {
                'is_attended': False,
                'name': scheduled_obj.subject.name,
                'teacher': teacher_name,
                'time': class_time,
                'user': {
                    'address': location
                }
            }
            student_obj = ClassroomAttendance.objects.filter(
                timetable__id=scheduled_obj.id).get(student=request.user.id)
            if student_obj.status != "ALPHA":
                res['is_attended'] = True

            return Response(res)
        return Response({'error': {
            'status': 404,
            'message': 'tidak ada kelas saat ini'
        }
        })

    def post(self, request):
        lecture = current_lecture(user_id=request.user.id)
        if lecture:
            timetable_id = lecture.id
            student_id = request.user.id
            latitude = request.data['lat']
            longitude = request.data['lng']
            token = request.data['token']
            # Check Token
            if token == lecture.token:
                print("disini token")
                # Check Coordinate
                if validation(lat=latitude, lng=longitude):
                    try:
                        time = datetime.datetime.now().time()
                        student = ClassroomAttendance.objects.filter(student=student_id).filter(
                            timetable=timetable_id,
                        ).filter(timetable__start_time__lte=time,
                                 timetable__end_time__gte=time).first()
                    except:
                        student = False
                    if student and student.status == "ALPHA":
                        student.status = "HADIR"
                        student.save()
                        return Response(
                            {'success': {
                                'status': 200,
                                'message': 'Anda Berhasil Absen',
                            }})
                    return Response({'error': {
                        'status': 409,
                        'message': 'Anda sudah absen'
                    }})
                return Response({
                    'error': {
                        'status': 403,
                        'message': 'Anda diluar titik point'
                    }
                })
            return Response({
                'error': {
                    'status': 403,
                    'message': 'Token anda salah'
                }
            })


class StudentDashboard(APIView):
    # /student/
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

        data = {'status_code': '000',
                'data': {'greet': greeting,
                         'name': request.user.first_name + " " + request.user.last_name,
                         'current_attendance': {},
                         'current_lecture': {}
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
            if request.user.groups.filter(name='student').exists():
                current = AttendanceTimetable.objects.all().filter(
                    date=datetime.date.today()).filter(role="MRD").first()
                data['current_attendance'] = {
                    'work_time': current.work_time,
                    'home_time': current.home_time,
                }
            return Response(data)
        except:
            return Response(data)


class StudentHistory(APIView):
    # /student/history/
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
                'name': f"{h.student.first_name} {h.student.last_name}",
                'username': h.student.username,
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


# class StudentPresenceList(APIView):
#     def get(self, request):
#         lectures = ClassroomTimetable.objects.all().filter(date=datetime.date.today())
#         data = {
#             'status_code': '000',
#             'message': "success",
#             'data': {'lectures': {}}
#         }

#         num = 0
#         for lecture in lectures:
#             num += 1
#             data['data']['lectures'][num] = {
#                 'name': lecture.subject.name,
#                 'start': lecture.start_time.strftime("%H:%M"),
#                 'end': lecture.end_time.strftime("%H:%M"),
#                 'teacher': "{} {}".format(lecture.subject.teacher.first_name, lecture.subject.teacher.last_name),

#             }

#         return Response(data)

# class StudentTimetables(APIView):
#     authentication_classes = [authentication.SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         timetables = ClassroomTimetable.objects.all()
#         data = {'status_code': '000',
#                 'message': "success", 'data': {

#                 }}
#         num = 0
#         for timetable in timetables:
#             num += 1
#             data['data'][num] = {
#                 'name': timetable.subject.name,
#                 'teacher': "{} {}".format(timetable.subject.teacher.first_name,  timetable.subject.teacher.last_name),
#                 'date': timetable.date,
#                 'start': timetable.start_time.strftime("%H:%M"),
#                 'end': timetable.end_time.strftime("%H:%M"),
#             }

#         return Response(data)
