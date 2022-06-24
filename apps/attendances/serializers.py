from wsgiref import validate
from rest_framework import serializers
from apps.attendances.models import Attendance, AttendanceTimetable


class AttendanceSerializer(serializers.Serializer):
    clock_in = serializers.TimeField()
    clock_out = serializers.TimeField()
    status = serializers.CharField()

    def create(self, validated_data):
        timetable = AttendanceTimetable.objects.get(
            id=validated_data['timetable'])
        attendance = Attendance(clock_in=validated_data['clock_in'],
                                clock_out=validated_data['clock_out'],
                                status=validated_data['status'], timetable=timetable)
        attendance.save()
        return attendance
