from django import forms
from django.core.validators import validate_ipv46_address

from .models import Camera, CameraSettings, CameraComsSettings


class CameraForm(forms.ModelForm):
    """
    This is the form for Adding a new camera to the system or editing its settings
    """
    class Meta:
        model = Camera
        fields = ["Camera_ip", "location", "camera_type"]

    def clean(self):
        super(CameraForm, self).clean()
        ip_address = self.cleaned_data.get('Camera_ip')

        if validate_ipv46_address(ip_address):
            self._errors['Camera_ip'] = self.error_class(['is not valid ip4 address'])


class UpdateSettings(forms.ModelForm):
    """
    This is the form that is used when editing the settings of a camera
    """
    class Meta:
        model = CameraSettings
        fields = ["fps", "face_detection", "profile_detection", "person_detection", "movement_detection",
                  "distance_guesser"]


class UpdateComsSettings(forms.ModelForm):
    """
    this is the form used when editing the communication settings of a camera
    """
    class Meta:
        model = CameraComsSettings
        fields = ["MQTT_broker", "MQTT_topic", "discord_webhook"]
