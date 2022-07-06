from requests import Response
from rest_framework.views import APIView
from apps.classrooms.models import ClassroomAttendance, ClassroomTimetable
from utils.gps import detector
from utils.shortcuts import current_lecture


class StudentPresence(APIView):
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
