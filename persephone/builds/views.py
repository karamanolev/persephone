from django.shortcuts import render
from django.urls.base import reverse_lazy
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
    success_url = reverse_lazy('index')
    template_name = 'project_form.html'
    fields = '__all__'


class APIProjects(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class APIProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class APIBuilds(generics.ListCreateAPIView):
    def get_queryset(self):
        return Project.objects.get(id=self.kwargs['project_id']).builds.all()

    serializer_class = BuildSerializer

    def perform_create(self, serializer):
        serializer.save(project=Project.objects.get(id=self.kwargs['project_id']))


class APIBuildDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Build.objects.all()
    serializer_class = BuildSerializer

    def get_object(self):
        return self.get_queryset().get(
            project=self.kwargs['project_id'], build_number=self.kwargs['build_number'])
