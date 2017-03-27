from django.conf.urls import url

from builds import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^projects/(\d+)/$', views.project, name='project'),
    url('^projects/create$', views.ProjectCreate.as_view(), name='project_create'),
    url('^projects/(\d+)/builds/(\d+)/$', views.project, name='build'),

    url('^api/v1/projects/$', views.APIProjects.as_view(), name='api_projects'),
    url('^api/v1/projects/(?P<pk>\d+)/$', views.APIProjectDetail.as_view(), name='api_project'),
    url('^api/v1/projects/(?P<project_id>\d+)/builds/$', views.APIBuilds.as_view(), name='api_builds'),
    url('^api/v1/projects/(?P<project_id>\d+)/builds/(?P<build_number>\d+)/$',
        views.APIBuildDetail.as_view(), name='api_build'),
]
