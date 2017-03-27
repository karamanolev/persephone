from rest_framework import serializers

from builds.models import Build, Project


class BuildSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Build
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    builds = BuildSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = '__all__'
