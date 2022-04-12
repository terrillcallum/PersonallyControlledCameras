import os
import urllib
import urllib.request
import cv2
import numpy as np
from django.db import models

from webcamstreams.ImageDetection import face_recognizer, detection_drawing, distance_guesser, profile_recognizer


class Camera(models.Model):
    IPCAM = "ipcam"
    PICAM = "picam"
    CAMERA_CHOICES = (
        (IPCAM, 'ipcam'),
        (PICAM, 'raspberry pi camera')
    )
    Camera_ip = models.TextField()
    photoString = models.TextField()
    location = models.TextField(default="undefined")
    camera_type = models.CharField(default="unknown", choices=CAMERA_CHOICES, max_length=10)

    def GetphotoString(self):
        new = self.photoString
        return new

    def pi_camera_image_grab(self):
        try:
            imgResp = urllib.request.urlopen(f"http://127.0.0.1:8000/webcam_capture/{self.Camera_ip}", timeout=2)
            imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
            img = cv2.imdecode(imgNp, -1)

        except TimeoutError:
            return ""
        #    img = cv2.imread(f"{os.getcwd()}/Camsystem/static/defaultimg.jpg", cv2.IMREAD_COLOR)
        img = self.run_detections(img)
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def ip_camera_image_grab(self):
        try:
            imgResp = urllib.request.urlopen(f"http://{self.Camera_ip}/capture", timeout=2)
            imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
            img = cv2.imdecode(imgNp, -1)

        except TimeoutError:
            img = cv2.imread(f"{os.getcwd()}/Camsystem/static/defaultimg.jpg", cv2.IMREAD_COLOR)
        self.run_detections(img)
        ret, jpeg = cv2.imencode('.jpg', img)
        self.photoString = jpeg.tobytes()
        self.save()

    def run_detections(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if self.camerasettings.face_detection == "SERVER":
            faceDetection = face_recognizer(gray)
            detection_drawing(img, faceDetection)
            if self.camerasettings.distance_guesser == "SERVER":
                distance_guesser(img, faceDetection)
        if self.camerasettings.profile_detection == "SERVER":
            LeftLookingDetection, RightLookingDetection = profile_recognizer(gray)
            detection_drawing(img, LeftLookingDetection, (0, 0, 255))
            detection_drawing(img, RightLookingDetection, (200, 100, 200))
        # if self.camerasettings.movement_detection == "SERVER":
        #    movement_detection(last_gray, gray, img, True)
        return img


class CameraSettings(models.Model):
    Camera = models.OneToOneField(
        Camera,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    stop = models.BooleanField(default=False)
    fps = models.BooleanField(default=False)
    INACTIVE = "INACTIVE"
    SERVER = "SERVER"
    CAMERA = "CAMERA"
    PROCESSING_CHOICES = (
        (INACTIVE, 'inactive'),
        (SERVER, 'server'),
        (CAMERA, 'camera'),
    )
    face_detection = models.CharField(default="inactive", choices=PROCESSING_CHOICES, max_length=10)
    profile_detection = models.CharField(default="inactive", choices=PROCESSING_CHOICES, max_length=10)
    person_detection = models.CharField(default="inactive", choices=PROCESSING_CHOICES, max_length=10)
    movement_detection = models.CharField(default="inactive", choices=PROCESSING_CHOICES, max_length=10)
    distance_guesser = models.CharField(default="inactive", choices=PROCESSING_CHOICES, max_length=10)


class CameraComsSettings(models.Model):
    Camera = models.OneToOneField(
        Camera,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    MQTT_broker = models.CharField(default="unknown", max_length=200)
    MQTT_topic = models.CharField(default="unknown", max_length=200)
    discord_webhook = models.CharField(default="unknown", max_length=200)
