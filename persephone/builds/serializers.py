from rest_framework import serializers

from builds.models import Build, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class BuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Build
        fields = '__all__'
