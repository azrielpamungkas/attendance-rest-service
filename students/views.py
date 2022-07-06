from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from students.serializers import StudentPresenceSer
from utils.gps import validation, detector
from utils.shortcuts import current_lecture, auto_now
from apps.classrooms.models import ClassroomTimetable, ClassroomAttendance
from apps.attendances.models import AttendanceTimetable
from drf_yasg.utils import swagger_auto_schema
from .docs import StudentDoc


doc = StudentDoc()


class StudentDashboard(APIView):
    @swagger_auto_schema(responses=doc.student_dashboard_get)
    def get(self, request, format=None):
        print(request.META.get("SESSION_MANAGER", "---"))
        if request.user.groups.filter(name="student").exists():
            lecture_obj = current_lecture(request.user.id, ClassroomTimetable)
            attendace_obj = (
                AttendanceTimetable.objects.all()
                .filter(date=auto_now("today"))
                .filter(role="MRD")
                .first()
            )
            subject = (lambda obj: None if obj is None else obj.subject.name)(
                lecture_obj
            )
            teacher_first_name = (
                lambda obj: None if obj is None else obj.subject.teacher.first_name
            )(lecture_obj)
            teacher_last_name = (
                lambda obj: None if obj is None else obj.subject.teacher.last_name
            )(lecture_obj)
            start_time = (
                lambda obj: None if obj is None else obj.start_time.strftime("%H:%M")
            )(lecture_obj)
            end_time = (
                lambda obj: None if obj is None else obj.end_time.strftime("%H:%M")
            )(lecture_obj)

            currentTime = auto_now()
            if currentTime.hour < 12:
                greeting = "Selamat Pagi"
            elif currentTime.hour < 15:
                greeting = "Selamat Siang"
            elif currentTime.hour < 18:
                greeting = "Selamat Sore"
            else:
                greeting = "Selamat Malam"

            res = {
                "greet": greeting,
                "currentLecture": {
                    "subject": subject,
                    "teacher": {
                        "first_name": teacher_first_name,
                        "last_name": teacher_last_name,
                    },
                    "time": {
                        "start_time": (lambda x: None if x is None else x)(start_time),
                        "end_time": (lambda x: None if x is None else x)(end_time),
                    },
                },
                "currentAttendance": {
                    "work_time": (lambda x: None if x is None else x.work_time)(
                        attendace_obj
                    ),
                    "home_time": (lambda x: None if x is None else x.home_time)(
                        attendace_obj
                    ),
                },
                "user": {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                },
            }
            return Response(res)
        raise PermissionDenied


class StudentSchedule(APIView):
    @swagger_auto_schema(responses=doc.student_schedule_get)
    def get(self, request):
        clasroom_timetable_qry = ClassroomTimetable.objects.filter(
            subject__classroom__student=request.user.id
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
                    )(obj.id, current_lecture(request.user.id, ClassroomTimetable)),
                    "subject": obj.subject.name,
                    "teacher": {
                        "first_name": obj.subject.teacher.first_name,
                        "last_name": obj.subject.teacher.last_name,
                    },
                    "start_time": obj.start_time,
                    "end_time": obj.end_time,
                }
            )
        return Response(res)


class StudentPresence(APIView):
    serializer_class = StudentPresenceSer

    @swagger_auto_schema(responses=doc.student_presence_get)
    def get(self, request):
        scheduled_obj = current_lecture(request.user.id, ClassroomTimetable)
        if scheduled_obj:
            class_time = "{} - {} WIB".format(
                scheduled_obj.start_time.strftime("%H:%M"),
                scheduled_obj.end_time.strftime("%H:%M"),
            )
            teacher_name = "{} {}".format(
                scheduled_obj.subject.teacher.first_name,
                scheduled_obj.subject.teacher.last_name,
            )
            res = {
                "is_attended": False,
                "name": scheduled_obj.subject.name,
                "teacher": teacher_name,
                "time": class_time,
                "user": {"address": detector(geo=self.request.query_params.get("geo"))},
            }
            student_obj = ClassroomAttendance.objects.filter(
                timetable__id=scheduled_obj.id
            ).get(student=request.user.id)
            if student_obj.status != "ALPHA":
                res["is_attended"] = True

            return Response(res)
        return Response(
            {"error": {"status": 404, "message": "tidak ada kelas saat ini"}}
        )

    @swagger_auto_schema(
        request_body=StudentPresenceSer, responses=doc.student_presence_post
    )
    def post(self, request):
        lecture = current_lecture(request.user.id, ClassroomTimetable)
        serializer = StudentPresenceSer(data=request.data)
        if lecture:
            if serializer.is_valid():
                timetable_id = lecture.id
                student_id = request.user.id
                lat = request.data["lat"]
                lng = request.data["lng"]
                token = request.data["token"]
                # Check Token
                if token == lecture.token:
                    # Check Coordinate
                    if validation(lat=lat, lng=lng):
                        time = auto_now("time")
                        student_obj = (
                            ClassroomAttendance.objects.filter(timetable=timetable_id)
                            .filter(
                                timetable__start_time__lte=time,
                                timetable__end_time__gte=time,
                            )
                            .get(student=student_id)
                        )
                        if student_obj.status == "ALPHA":
                            student_obj.status = "HADIR"
                            student_obj.save()
                            return Response(
                                {
                                    "success": {
                                        "status": 200,
                                        "message": "Anda Berhasil Absen",
                                    }
                                },
                                status=status.HTTP_200_OK,
                            )
                        return Response(
                            {"error": {"status": 409, "message": "Anda sudah absen"}},
                            status=status.HTTP_409_CONFLICT,
                        )
                    return Response(
                        {
                            "error": {
                                "status": 403,
                                "message": "Anda diluar titik point",
                            }
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                return Response(
                    {"error": {"status": 403, "message": "Token anda salah"}},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"error": {"status": 401, "message": "Tidak ada kelaas"}},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class StudentHistory(APIView):
    @swagger_auto_schema(responses=doc.student_history_get)
    def get(self, request):
        lecture_histories = ClassroomAttendance.objects.filter(student=request.user.id)
        if lecture_histories != None:
            res = {
                "user": {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "username": request.user.username,
                }
            }
            for history in lecture_histories:
                month_year = "{} {}".format(
                    history.timetable.date.strftime("%b"), history.timetable.date.year
                )
                res.setdefault(month_year, [])
                res[month_year].append(
                    {
                        "name": history.timetable.subject.name,
                        "date": history.timetable.date,
                        "status": history.status,
                    }
                )
            return Response(res)
        return Response()


class StudentStatistic(APIView):
    @swagger_auto_schema(responses=doc.student_statistic_get)
    def get(self, request):
        timetable_cnt = ClassroomTimetable.objects.filter(
            date__lte=auto_now("today")
        ).count()
        attendance_qry = ClassroomAttendance.objects.filter(
            student=request.user.id
        ).filter(timetable__date__lte=auto_now("today"))
        presence = (lambda x, y: 1.0 if x or y == 0 else 1.0 - x / y)(
            attendance_qry.filter(status="ALPHA").count(), timetable_cnt
        )
        leave = (lambda x, y: 0 if x or y == 0 else x / y)(
            attendance_qry.filter(status="IJIN").count(), timetable_cnt
        )
        absent = (lambda x, y: 0 if x or y == 0 else x / y)(
            attendance_qry.filter(status="ALPHA").count(), timetable_cnt
        )
        res = {
            "leave": leave,
            "absent": absent,
            "presence": presence,
            "indicator": (
                lambda x: "Aman" if x > 0.8 else ("Rawan" if x > 0.7 else "Bahaya")
            )(presence),
        }
        return Response(res)
