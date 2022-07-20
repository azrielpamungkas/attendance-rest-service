from rest_framework import serializers
from .models import Attendance, Leave


class AttendanceSer(serializers.ModelSerializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()

    class Meta:
        model = Attendance
        fields = ["lat", "lng"]


class LeaveHalfSer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = (
            "user",
            "leave_type",
            "classroom_scheduled",
            "reason",
            "attachment",
            "leave_mode",
        )


class LeaveFullSer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = (
            "user",
            "leave_type",
            "attendance_scheduled",
            "reason",
            "attachment",
            "leave_mode",
        )
