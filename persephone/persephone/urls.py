"""persephone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.urls import path, re_path

from persephone import views

urlpatterns = [
    url('^accounts/', include('allauth.urls')),
    path('api/v1/login', views.APILogin.as_view(), name='login'),
    path('api/v1/logout', views.APILogout.as_view(), name='logout'),
    path('api/v1/', include('builds.urls', namespace='builds')),
    re_path('.*', views.react_host),
]
