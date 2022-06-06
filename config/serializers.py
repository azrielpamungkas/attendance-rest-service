from sqlite3 import Time
from tokenize import blank_re
from rest_framework import serializers
from attendances.models import StudentAttendance
from timetables.models import Timetable


class Test(serializers.Serializer):
    comments = serializers.IntegerField()
    likes = serializers.IntegerField()


class SubmitAttendanceSerializer(serializers.Serializer):
    STATUS = (
        ('ALPHA', 'ALPHA'),
        ('HADIR', 'HADIR'),
        ('IJIN', 'IJIN'),
    )
    name = serializers.CharField(read_only=True)
    token = serializers.CharField()
    status = serializers.ChoiceField(choices=STATUS)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    timetable = serializers.PrimaryKeyRelatedField(read_only=True,)
    #    queryset=Timetable.objects.all(),)

    def create(self, validated_data):
        return StudentAttendance.objects.create(**validated_data)
