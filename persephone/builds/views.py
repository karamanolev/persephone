from django.shortcuts import render
from django.urls.base import reverse
from django.views.generic.edit import CreateView
from rest_framework import generics

from builds.models import Build, Project
from builds.serializers import BuildSerializer, ProjectSerializer


def index(request):
    data = {
        'projects': Project.objects.all(),
    }
    return render(request, 'index.html', data)


def project(request, project_id):
    pass


class ProjectCreate(CreateView):
    model = Project
    success_url = 'index'
    template_name = 'project_form.html'
    fields = '__all__'


class APIProjects(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class APIProjectDetail(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class APIBuildDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Build.objects.all()
    serializer_class = BuildSerializer
