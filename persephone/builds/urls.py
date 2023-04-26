from django.urls import path

from builds import views

app_name = 'builds'

urlpatterns = [
    path('', views.index, name='index'),
    path('global-settings', views.global_settings, name='global_settings'),
    path('domain-not-allowed', views.domain_not_allowed, name='domain_not_allowed'),
    path('projects/create', views.ProjectCreate.as_view(), name='project_create'),
    path('projects/<int:project_id>/', views.project, name='project'),
    path('projects/<int:pk>/delete', views.ProjectDelete.as_view(), name='project_delete'),
    path('projects/<int:pk>/edit', views.ProjectUpdate.as_view(), name='project_update'),
    path('projects/<int:project_id>/builds/<int:build_id>/', views.build_detail, name='build'),
    path('projects/<int:project_id>/builds/<int:build_id>/delete', views.build_delete, name='build_delete'),
    path('projects/<int:project_id>/builds/<int:build_id>/approve',
        views.build_action('approve'), name='build_approve'),
    path('projects/<int:project_id>/builds/<int:build_id>/reject',
        views.build_action('reject'), name='build_reject'),
    path('projects/<int:project_id>/builds/<int:build_id>/screenshots/<int:screenshot_id>/image',
        views.screenshot_image, name='screenshot_image'),
    path('projects/<int:project_id>/builds/<int:build_id>/screenshots/<int:screenshot_id>/diff',
        views.screenshot_image_diff, name='screenshot_image_diff'),

    path('api/v1/projects/', views.APIProjects.as_view(), name='api_projects'),
    path('api/v1/projects/<int:pk>/', views.APIProjectDetail.as_view(), name='api_project'),
    path('api/v1/projects/<int:project_id>/builds/',
        views.APIBuilds.as_view(), name='api_builds'),
    path('api/v1/projects/<int:project_id>/builds/<int:build_id>/',
        views.APIBuildDetail.as_view(), name='api_build'),
    path('api/v1/projects/<int:project_id>/builds/<int:build_id>/finish',
        views.APIBuildFinish.as_view(), name='api_build_finish'),
    path('api/v1/projects/<int:project_id>/builds/<int:build_id>/fail',
        views.APIBuildFail.as_view(), name='api_build_fail'),
    path('api/v1/projects/<int:project_id>/builds/<int:build_id>/screenshots/',
        views.APIScreenshots.as_view(), name='api_build'),
    path('api/v1/projects/<int:project_id>/builds/<int:build_id>/screenshots/<str:screenshot_name>',
        views.APIScreenshotDetail.as_view(), name='api_build'),
]
