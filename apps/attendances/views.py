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
            date=datetime.date.today()).filter(role=role).first()
        return current
    except:
        return None


class AttendanceView(APIView):
    serializer_class = serializers.AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        response = {}
        if request.user.groups.filter(name='student').exists():
            current = current_attendance('MRD')
            print(current)
            if current != None:
                response['data'] = {"role": current.role, "date": current.date, 'work_time': current.work_time,
                                    'home_time': current.home_time}
                try:
                    obj = Attendance.objects.all().filter(
                        user=request.user.id,
                        timetable__date=datetime.date.today()).first()
                    response['data']['clock_in'] = obj.clock_in
                    response['data']['clock_out'] = obj.clock_out
                    return Response(response)
                except:
                    response['data']['clock_in'] = "--:--"
                    response['data']['clock_out'] = "--:--"
                    return Response(response)
        return Response({'error': 'tidak ada kelas', 'data': {
            'work_time': '--:--',
            'home_time': '--:--',
            'clock_in': '--:--',
            'clock_out': '--:--'
        }})

    def post(self, request):
        if request.user.groups.filter(name='student').exists():
            current = current_attendance('MRD')
        submit_data = request.data.copy()
        print(submit_data)
        submit_data['clock_in'] = datetime.datetime.now().time()
        serializer = serializers.AttendanceSerializer(data=submit_data)
        if serializer.is_valid():
            try:
                serializer.save(timetable=current.id)
                return Response(serializer.data)
            except:
                return Response('tidak ada kelas')
        return Response(serializer.errors)
