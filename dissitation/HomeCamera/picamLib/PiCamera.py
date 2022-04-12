import json
import socket
import time

import cv2
import requests


class PiCamera:
    """
    This class acts as the camera itself and contains all the code related to the camera
    """

    def __init__(self):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.ip = socket.gethostbyname(socket.gethostname())
        self.prev_frame_time = time.time()
        self.new_frame_time = time.time()
        self.stream = cv2.VideoCapture(0)
        self.stopped = False
        self.frame = ""
        self.error = ""
        self.settings = {
            "stop": False,
            "fps": False,
            "person_detection": "INACTIVE",
            "face_detection": "INACTIVE",
            "distance_guesser": "INACTIVE",
            "profile_detection": "INACTIVE",
            "movement_detection": "INACTIVE",
            "discord_webhook": "unknown",
            "mqttbroker": "unknown",
            "mqtttopic": "unknown",

        }

    def fps(self):
        return 1 / (self.new_frame_time - self.prev_frame_time)

    def update(self):
        """
        grabs a new image from the camera
        """
        self.prev_frame_time = self.new_frame_time
        grabbed, captured_frame = self.stream.read()
        if not grabbed:
            print("camera is not connected")
            self.error += "cant access camera"
            self.stop()
        self.new_frame_time = time.time()
        self.frame = captured_frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def collect_settings(self):
        url = f'http://localhost:8000/settings/{self.ip}'  # camera_streams/'
        try:
            data = json.loads(requests.get(url).text)
            self.settings = data

        except json.JSONDecodeError:
            print("Camera not set up on server or settings API not returning json")

        except requests.ConnectionError:
            print("cannot connect to API try changing local port/ip of server")
