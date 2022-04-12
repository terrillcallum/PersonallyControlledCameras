"""CamSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

import webcamstreams.views
from webcamstreams.forms import UpdateSettings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cams/', webcamstreams.views.camera_streams, name='camera_streams'),
    path('update_photo', webcamstreams.views.update_photo, name='update_photo'),
    path('addCamera', webcamstreams.views.add_camera, name='addCamera'),
    path('manageCamera', webcamstreams.views.manage_camera, name='manageCamera'),
    path('webcam_feed/<ip>', webcamstreams.views.webcam_feed, name='webcam_feed'),
    path('webcam_capture/<ip>', webcamstreams.views.webcam_capture, name='webcam_capture'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('settings/<ip>', webcamstreams.views.settings, name='settings'),
    path('retrieve_photo/<ip>', webcamstreams.views.retrieve_photo, name='retrieve_photo'),
    path('edit_settings_by_ip/<ip>/', webcamstreams.views.edit_settings_by_ip, name='update_cam'),
    path('edit_coms_settings_by_ip/<ip>/', webcamstreams.views.edit_coms_settings_by_ip, name='update_cam_coms'),
    path('move_camera/<ip>/', webcamstreams.views.move_camera, name='move_camera'),
]
