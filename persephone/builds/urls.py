from django.urls import path

from builds import views

app_name = 'builds'

urlpatterns = [
    path('projects', views.APIProjects.as_view(), name='projects'),
    path('projects/<int:pk>', views.APIProjectDetail.as_view(), name='project'),
    path('projects/<int:project_id>/builds', views.APIBuilds.as_view(), name='builds'),

    path('projects/<int:project_id>/builds/<int:build_id>',
         views.APIBuildDetail.as_view(), name='build'),
    path('projects/<int:project_id>/builds/<int:build_id>/finish',
         views.APIBuildFinish.as_view(), name='build_finish'),
    path('projects/<int:project_id>/builds/<int:build_id>/fail',
         views.APIBuildFail.as_view(), name='build_fail'),
    path('projects/<int:project_id>/builds/<int:build_id>/screenshots',
         views.APIScreenshots.as_view(), name='build'),
    path('projects/<int:project_id>/builds/<int:build_id>/screenshots/<path:name>/image',
         views.screenshot_image, name='screenshot_image'),
    path('projects/<int:project_id>/builds/<int:build_id>/screenshots/<path:name>/diff',
         views.screenshot_image_diff, name='screenshot_image_diff'),
    path('projects/<int:project_id>/builds/<int:build_id>/screenshots/<path:name>',
         views.APIScreenshotDetail.as_view(), name='screenshot_details'),
]
