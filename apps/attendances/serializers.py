from dataclasses import field
from rest_framework import serializers
from .models import Attendance


class AttendanceSer(serializers.ModelSerializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()

    class Meta:
        model = Attendance
        fields = ["lat", "lng"]
