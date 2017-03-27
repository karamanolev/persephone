from django.conf.urls import url

from builds import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^projects/$', views.builds, name='projects'),
    url('^projects/(\d+)/$', views.builds, name='project'),
    url('^projects/(\d+)/builds/(\d+)/$', views.builds, name='build'),

    url('^api/v1/projects/$', views.APIProjects.as_view(), name='api_projects'),
    url('^api/v1/projects/(\d+)/$', views.APIProjectDetail.as_view(), name='api_project'),
    url('^api/v1/projects/(\d+)/builds/(\d+)/$', views.APIBuildDetail.as_view(), name='api_build'),
]
