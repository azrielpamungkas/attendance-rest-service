from rest_framework import serializers


class TeacherJournalSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=240)

    class Meta:
        fields = "__all__"
