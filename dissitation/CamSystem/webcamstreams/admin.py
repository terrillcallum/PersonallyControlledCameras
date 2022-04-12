from django.contrib import admin
from .models import Camera, CameraSettings, CameraComsSettings

# Register your models here.
admin.site.register(Camera)
admin.site.register(CameraSettings)
admin.site.register(CameraComsSettings)
