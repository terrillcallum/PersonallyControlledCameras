from django.contrib import admin
from .models import Camera, CameraSettings, CameraComsSettings

"""
This page is used to add models in the database to the Django admin manager
"""

# Register your models here.
admin.site.register(Camera)
admin.site.register(CameraSettings)
admin.site.register(CameraComsSettings)
