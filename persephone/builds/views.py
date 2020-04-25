from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.http.response import HttpResponseForbidden, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from builds import tasks
from builds.forms import GlobalSettingsForm
from builds.models import Build, Project, Screenshot
from builds.serializers import BuildSerializer, ProjectSerializer, ScreenshotSerializer, \
    FullBuildSerializer
from builds.utils import sort_screenshots_by_relevance


def domain_not_allowed(request):
    return render(request, 'domain_not_allowed.html')


@login_required
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
    project_obj = Project.objects.get(id=project_id)
    active_builds = project_obj.builds.filter(
        archived=False,
        state__in=[Build.STATE_INITIALIZING, Build.STATE_RUNNING, Build.STATE_FINISHING,
                   Build.STATE_PENDING_REVIEW],
    )
    active_build_ids = active_builds.values_list('id', flat=True)
    past_builds = project_obj.builds.exclude(id__in=active_build_ids)
    data = {
        'project': project_obj,
        'active_builds': active_builds,
        'past_builds': past_builds,
    }
    return render(request, 'project.html', data)


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
def screenshot_image(request, project_id, build_id, name):
    build = Build.objects.get(project_id=project_id, id=build_id)
    screenshot = build.screenshots.get(name=name)
    if not screenshot.image:
        raise Http404()
    resp = HttpResponse(open(screenshot.image.path, 'rb'), content_type='image/png')
    resp['Cache-Control'] = 'public, max-age=600'
    return resp


@login_required
def screenshot_image_diff(request, project_id, build_id, name):
    build = Build.objects.get(project_id=project_id, id=build_id)
    screenshot = build.screenshots.get(name=name)
    if not screenshot.image_diff:
        raise Http404()
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
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Build.objects.filter(project_id=self.kwargs['project_id'])

    def perform_create(self, serializer):
        build = serializer.save(project=Project.objects.get(id=self.kwargs['project_id']))
        transaction.on_commit(lambda: tasks.process_build_created(build.id))


class APIBuildDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FullBuildSerializer

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
        transaction.on_commit(lambda: tasks.process_build_finished(build.id))
        return Response(BuildSerializer(build).data)


class APIBuildFail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, project_id, build_id):
        build = Build.objects.get(project_id=project_id, id=build_id)
        if build.state != Build.STATE_RUNNING:
            return HttpResponseForbidden()
        build.state = Build.STATE_FAILING
        build.save()
        transaction.on_commit(lambda: tasks.process_build_failed(build.id))
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
        transaction.on_commit(lambda: tasks.process_screenshot(screenshot.id))
        return Response(ScreenshotSerializer(screenshot).data)


class APIScreenshotDetail(generics.RetrieveDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ScreenshotSerializer

    def get_object(self):
        return Screenshot.objects.get(
            build_id=self.kwargs['build_id'],
            build__project_id=self.kwargs['project_id'],
            name=self.kwargs['name'],
        )
