from dataclasses import field
from rest_framework import serializers
from apps.classrooms.models import ClassroomAttendance


class StudentPresenceSer(serializers.ModelSerializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    token = serializers.CharField()

    class Meta:
        model = ClassroomAttendance
        fields = ["lat", "lng", "token"]
