from django.conf.urls import url

from builds import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^projects/create$', views.ProjectCreate.as_view(), name='project_create'),
    url('^projects/(\d+)/$', views.project, name='project'),
    url('^projects/(?P<pk>\d+)/delete$', views.ProjectDelete.as_view(), name='project_delete'),
    url('^projects/(?P<pk>\d+)/edit$', views.ProjectUpdate.as_view(), name='project_update'),
    url('^projects/(\d+)/builds/(\d+)/$', views.build_detail, name='build'),
    url('^projects/(\d+)/builds/(\d+)/delete$', views.build_delete, name='build_delete'),
    url('^projects/(\d+)/builds/(\d+)/approve$',
        views.build_action('approve'), name='build_approve'),
    url('^projects/(\d+)/builds/(\d+)/reject$',
        views.build_action('reject'), name='build_reject'),
    url('^projects/(\d+)/builds/(\d+)/screenshots/(.*)/image$',
        views.screenshot_image, name='screenshot_image'),
    url('^projects/(\d+)/builds/(\d+)/screenshots/(.*)/diff$',
        views.screenshot_image_diff, name='screenshot_image_diff'),

    url('^api/v1/projects/$', views.APIProjects.as_view(), name='api_projects'),
    url('^api/v1/projects/(?P<pk>\d+)/$', views.APIProjectDetail.as_view(), name='api_project'),
    url('^api/v1/projects/(?P<project_id>\d+)/builds/$',
        views.APIBuilds.as_view(), name='api_builds'),
    url('^api/v1/projects/(?P<project_id>\d+)/builds/(?P<build_id>\d+)/$',
        views.APIBuildDetail.as_view(), name='api_build'),
    url('^api/v1/projects/(?P<project_id>\d+)/builds/(?P<build_id>\d+)/finish$',
        views.APIBuildFinish.as_view(), name='api_build_finish'),
    url('^api/v1/projects/(?P<project_id>\d+)/builds/(?P<build_id>\d+)/fail$',
        views.APIBuildFail.as_view(), name='api_build_fail'),
    url('^api/v1/projects/(?P<project_id>\d+)/builds/(?P<build_id>\d+)/screenshots/$',
        views.APIScreenshots.as_view(), name='api_build'),
    url('^api/v1/projects/(?P<project_id>\d+)/builds/'
        '(?P<build_id>\d+)/screenshots/(?P<screenshot_name>.*)$',
        views.APIScreenshotDetail.as_view(), name='api_build'),
]
