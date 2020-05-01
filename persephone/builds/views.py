from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http.response import HttpResponseForbidden, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls.base import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from builds import tasks
from builds.forms import GlobalSettingsForm
from builds.models import Build, Project, Screenshot
from builds.serializers import BuildSerializer, ProjectSerializer, ScreenshotSerializer
from builds.utils import sort_screenshots_by_relevance


@login_required
def index(request):
    data = {
    }
    return render(request, 'index.html', data)


def domain_not_allowed(request):
    return render(request, 'domain_not_allowed.html')


def global_settings(request):
    if request.method == 'GET':
        form = GlobalSettingsForm(request=request)
    elif request.method == 'POST':
        form = GlobalSettingsForm(request=request, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('builds:global_settings')
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
    data = {
        'form': form,
    }
    return render(request, 'global_settings.html', data)


@login_required
def project(request, project_id):
    project = Project.objects.get(id=project_id)
    active_builds = project.builds.filter(
        archived=False,
        state__in=[Build.STATE_INITIALIZING, Build.STATE_RUNNING, Build.STATE_FINISHING,
                   Build.STATE_PENDING_REVIEW],
    )
    active_build_ids = active_builds.values_list('id', flat=True)
    past_builds = project.builds.exclude(id__in=active_build_ids)
    data = {
        'project': project,
        'active_builds': active_builds,
        'past_builds': past_builds,
    }
    return render(request, 'project.html', data)


class ProjectCreate(CreateView, LoginRequiredMixin):
    model = Project
    success_url = reverse_lazy('builds:index')
    template_name = 'project_form.html'
    fields = '__all__'


class ProjectUpdate(UpdateView, LoginRequiredMixin):
    model = Project
    success_url = reverse_lazy('builds:index')
    template_name = 'project_form.html'
    fields = '__all__'


class ProjectDelete(DeleteView, LoginRequiredMixin):
    model = Project
    success_url = reverse_lazy('builds:index')
    fields = '__all__'


@login_required
def build_detail(request, project_id, build_id):
    build = Build.objects.get(project_id=project_id, id=build_id)
    screenshots = list(build.screenshots.all())
    sort_screenshots_by_relevance(screenshots)
    data = {
        'build': build,
        'screenshots': screenshots,
        'num_matching': sum(1 for s in screenshots if s.state == Screenshot.STATE_MATCHING)
    }
    return render(request, 'build.html', data)


@login_required
def build_delete(request, project_id, build_id):
    build = Build.objects.get(project_id=project_id, id=build_id)
    build.delete()
    return redirect('builds:project', project_id)


def build_action(action):
    @login_required
    def _build_status(request, project_id, build_id):
        build = Build.objects.get(project_id=project_id, id=build_id)
        if build.state not in [Build.STATE_PENDING_REVIEW,
                               Build.STATE_APPROVED,
                               Build.STATE_REJECTED]:
            return HttpResponseForbidden()
        if action == 'approve':
            build.state = Build.STATE_APPROVED
            build.date_approved = timezone.now()
        elif action == 'reject':
            build.state = Build.STATE_REJECTED
            build.date_rejected = timezone.now()
        else:
            raise Exception('Unknown action {}'.format(action))
        build.reviewed_by = request.user.email or request.user.username
        build.save()
        build.update_github_status()
        return redirect('builds:build', project_id, build_id)

    return _build_status


@login_required
def screenshot_image(request, project_id, build_id, screenshot_name):
    build = Build.objects.get(project_id=project_id, id=build_id)
    screenshot = build.screenshots.get(name=screenshot_name)
    resp = HttpResponse(open(screenshot.image.path, 'rb'), content_type='image/png')
    resp['Cache-Control'] = 'public, max-age=600'
    return resp


@login_required
def screenshot_image_diff(request, project_id, build_id, screenshot_name):
    build = Build.objects.get(project_id=project_id, id=build_id)
    screenshot = build.screenshots.get(name=screenshot_name)
    resp = HttpResponse(open(screenshot.image_diff.path, 'rb'), content_type='image/png')
    resp['Cache-Control'] = 'public, max-age=600'
    return resp


class APIProjects(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class APIProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class APIBuilds(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BuildSerializer

    def get_queryset(self):
        return Build.objects.filter(project_id=self.kwargs['project_id'])

    def perform_create(self, serializer):
        build = serializer.save(project=Project.objects.get(id=self.kwargs['project_id']))
        transaction.on_commit(lambda: tasks.process_build_created.delay(build.id))


class APIBuildDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BuildSerializer

    def get_object(self):
        return Build.objects.get(
            project=self.kwargs['project_id'], id=self.kwargs['build_id'])


class APIBuildFinish(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, project_id, build_id):
        build = Build.objects.get(project_id=project_id, id=build_id)
        if build.state != Build.STATE_RUNNING:
            return HttpResponseForbidden()
        build.state = Build.STATE_FINISHING
        build.save()
        transaction.on_commit(lambda: tasks.process_build_finished.delay(build.id))
        return Response(BuildSerializer(build).data)


class APIBuildFail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, project_id, build_id):
        build = Build.objects.get(project_id=project_id, id=build_id)
        if build.state != Build.STATE_RUNNING:
            return HttpResponseForbidden()
        build.state = Build.STATE_FAILING
        build.save()
        transaction.on_commit(lambda: tasks.process_build_failed.delay(build.id))
        return Response(BuildSerializer(build).data)


class APIScreenshots(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, project_id, build_id):
        build = Build.objects.get(project_id=project_id, id=build_id)
        if build.state not in [Build.STATE_INITIALIZING, Build.STATE_RUNNING]:
            return HttpResponseForbidden()
        name = request.POST['name']

        build.screenshots.filter(name=name).delete()
        screenshot = Screenshot.objects.create(
            build=build,
            name=name,
            image=request.FILES['image'],
            metadata_json=request.POST.get('metadata'),
        )
        transaction.on_commit(lambda: tasks.process_screenshot.delay(screenshot.id))
        return Response(ScreenshotSerializer(screenshot).data)


class APIScreenshotDetail(generics.RetrieveDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ScreenshotSerializer

    def get_object(self):
        build = Build.objects.get(project_id=self.kwargs['project_id'], id=self.kwargs['build_id'])
        return build.screenshots.get(name=self.kwargs['screenshot_name'])
