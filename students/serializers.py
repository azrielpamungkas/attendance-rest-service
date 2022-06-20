from rest_framework import serializers
from apps.classrooms.models import ClassroomAttendance


class SubmitAttendanceSerializer(serializers.Serializer):
    STATUS = (
        ('ALPHA', 'ALPHA'),
        ('HADIR', 'HADIR'),
        ('IJIN', 'IJIN'),
    )
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    token = serializers.CharField()
    status = serializers.ChoiceField(choices=STATUS)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    timetable = serializers.PrimaryKeyRelatedField(read_only=True,)

    def create(self, validated_data):
        return ClassroomAttendance.objects.create(**validated_data)
