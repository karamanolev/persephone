from django.shortcuts import render
from rest_framework import generics

from builds.models import Build, Project
from builds.serializers import BuildSerializer, ProjectSerializer


def index(request):
    return render(request, 'index.html')


def builds(request):
    pass


class APIProjects(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class APIProjectDetail(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class APIBuildDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Build.objects.all()
    serializer_class = BuildSerializer
