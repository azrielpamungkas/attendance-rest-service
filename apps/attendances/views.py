from rest_framework.views import APIView

from . import serializers
from .models import Attendance, AttendanceTimetable
from rest_framework.response import Response
from rest_framework import permissions
import datetime
# Create your views here.


def current_attendance(role):
    try:
        current = AttendanceTimetable.objects.all().filter(
            date=datetime.date.today()
        ).filter(role=role).first()
        print(current)
        return current
    except:
        return None


class AttendanceView(APIView):
    serializer_class = serializers.AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.groups.filter(name='student').exists():
            current = current_attendance('MRD')
        response = {"role": current.role, "date": current.date, 'work_time': current.work_time,
                    'home_time': current.home_time}
        return Response(response)

    def post(self, request):
        if request.user.groups.filter(name='student').exists():
            current = current_attendance('MRD')
        submit_data = request.data.copy()
        serializer = serializers.AttendanceSerializer(data=submit_data)
        if serializer.is_valid():
            serializer.save(timetable=current.id)
            return Response(serializer.data)
        return Response(serializer.errors)
