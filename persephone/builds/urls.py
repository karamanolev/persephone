from django.conf.urls import url

from builds import views

urlpatterns = [
    url('^$', views.index, name='index'),
]
