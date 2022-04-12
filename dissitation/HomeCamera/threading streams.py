# import the necessary packages
# import the Queue class from Python 3
import base64
import os
import socket
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from queue import Queue
from threading import Thread

import requests
from discordwebhook import Discord

first_frame = None
directory = os.path.join(os.getcwd(), '''IMAGES''')
os.chdir(directory)

def face_recognizer(grey_img):
    """
    function that returns the x and y of the face on the image and the width and height of the face
    uses a haarcascade xml file to guess the faces.
    note: only recognises faces from front on.
    """
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(grey_img, scaleFactor=1.15, minNeighbors=13)
    return faces


def detection_drawing(img, detections, colour=(255, 0, 60)):
    """
    draws a box on the image for each of the detections
    :param img: the image that is being drawn on
    :param detections: the detections found as tuples (x coord, y coord, width, height)
    :param colour: the colour of the box drawn
    """
    for x, y, w, h in detections:
        img = cv2.rectangle(img, (x, y), (x + w, y + h), colour, 4)


def distance_guesser(img, detections):
    """
    guesses the distance of a persons face by measuring their face size and comparing it to average detected face size
    :param img: the frame being used
    :param detections: where the detections are located
    :return: adds text to the images
    """
    contact = []
    for x, y, w, h in detections:
        imgHeight, imgWidth, ignore = img.shape
        distance = (16 * imgWidth) / w  # 655.6
        contact.append([float(distance), float(x + (0.5 * w)), float(y + (0.5 * h))])

        cv2.putText(img, f'{distance} CM', (x + 12, y - 13), cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                    (0, 0, 0), 2)


def profile_recognizer(grey_img):
    """
    detects the sides of the faces only recognizes looking one way so image is reverse and
    detections ran again to detect facing other way
    :param grey_img: takes in the grey scale version of the image
    :return: any detections in a tuple format
    """
    face_cascade = cv2.CascadeClassifier("haarcascade_profileface.xml")
    LeftLooking = face_cascade.detectMultiScale(grey_img, scaleFactor=1.15, minNeighbors=9)
    flipped = cv2.flip(grey_img, 1)
    RightLooking = face_cascade.detectMultiScale(flipped, scaleFactor=1.15, minNeighbors=9)
    for detection in range(len(RightLooking)):
        height, width = grey_img.shape
        RightLooking[detection][0] = width - RightLooking[detection][0] - RightLooking[detection][2]

    return LeftLooking, RightLooking


def movement_detection(grey_img, img, Draw_boxes=False, colour=(0, 200, 0)):
    """
    detects movement from the camera and reports it back
    """
    movement_detected = False
    # smooths the image to make it so that differences are slightly larger and smaller contours
    # do not have to be processed
    blurredGray = cv2.GaussianBlur(grey_img, (21, 21), 0)
    global first_frame
    if first_frame is None:
        first_frame = blurredGray

    # the delta frame will tell the colour difference between the old frame and the new frame,
    # as it is grey scale this will be a single number
    delta_frame = cv2.absdiff(first_frame, gray)
    # threshold will turn any difference number above a certain amount into white rest will be black
    thresh_frame = cv2.threshold(delta_frame, 55, 255, cv2.THRESH_BINARY)[1]
    # makes the white areas slightly larger this will connect areas of moving objects making detection better
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
    first_frame = blurredGray

    # uncomment too see detection clearer
    # cv2.imshow("Threshold Frame", thresh_frame)
    (conts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    imgHeight, imgWidth = grey_img.shape
    totalPix = imgHeight * imgWidth
    for contour in conts:
        # only show contours bigger then a certain size to get rid of any small differences (such as a leaf moving)
        if cv2.contourArea(contour) > (totalPix * 0.007):
            movement_detected = True
            if Draw_boxes:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), colour, 1)
    return movement_detected


def post_to_api(img_to_post):
    """
    this posts up the image that was taken to the webserver
    the image is turned into base64 then transmitted in a json dictionary format
    """
    global HostName
    ip_address = socket.gethostbyname(HostName)
    # url = 'https://localhost:5001/Videostreaming/CameraRecording'
    url = 'http://localhost:8000/' #camera_streams/'
    # url = 'http://jerboaworkshop.com/Videostreaming/CameraRecording'
    myimage = cv2.imencode('.jpeg', img_to_post)[1].tobytes()
    base64img = base64.b64encode(myimage)
    try:
        requests.post(url, data=dict(Photo=base64img, Device=ip_address), verify=False)
    except requests.ConnectionError:
        print("cannot connect to API")


def post_to_discord_webhook(img, url, camera_name):
    """
    post to a discord api webhook
    will allow for a image that has a detection to be posted into a discord channel
    """
    global last_face_detection
    global Webhook_detection_timer

    if (datetime.now() - last_face_detection).total_seconds() > Webhook_detection_timer:
        cv2.imwrite('temp.jpg', img)
        discord_webhook = Discord(url=url)
        discord_webhook.post(
            username=camera_name,
            avatar_url="https://avatars2.githubusercontent.com/u/38859131?s=460&amp;v=4",
            embeds=[
                {
                    "author": {
                        "name": camera_name,
                        "url": "",
                        "icon_url": "https://picsum.photos/24/24",
                    },
                    "title": "Camera",
                    "description": "Camera has made a detection",
                    "fields": [
                        {"name": "Field Name 1", "value": "Value 1", "inline": True},
                        {"name": "Field Name 2", "value": "Value 2", "inline": True},
                        {"name": "Field Name 3", "value": "Field Value 3"},
                    ],
                    "thumbnail": {"url": ""},
                    "footer": {
                        "text": "Embed Footer",
                        "icon_url": "https://picsum.photos/20/20",
                    },
                }
            ],
            file={
                "screenshot": open("temp.jpg", "rb"),
            }
        )
    return

class FileVideoStream:
    def __init__(self, queueSize=6):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(0)
        self.stopped = False
        # initialize the queue used to store frames read from
        # the video file
        self.Q = Queue(maxsize=queueSize)

    def start(self):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                return
            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                (grabbed, frame) = self.stream.read()
                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stop()
                    return
                # add the frame to the queue
                self.Q.put(frame)

    def read(self):
        # return next frame in the queue
        return self.Q.get()


    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


# import the necessary packages
import time
import cv2

# start the file video stream thread and allow the buffer to
# start to fill
print("[INFO] starting video file thread...")
fvs = FileVideoStream().start()
# loop over frames from the video file stream

prev_frame_time = time.time()
new_frame_time = time.time()

while True:
    # grab the frame from the threaded video file stream, resize
    # it, and convert it to grayscale (while still retaining 3
    # channels)
    prev_frame_time =  new_frame_time
    frame = fvs.read()
    new_frame_time = time.time()
    #frame = imutils.resize(frame, width=450)
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #frame = np.dstack([frame, frame, frame])
    # display the size of the queue on the frame
    #cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()),
    #            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    # show the frame and update the FPS counter

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    with ThreadPoolExecutor(max_workers=4) as pool:
        faceDetection = pool.submit(face_recognizer, gray)
        profile_reg_thread = pool.submit(profile_recognizer, gray)
        pool.submit(movement_detection, gray, frame, True)
        pool.submit(detection_drawing, frame, faceDetection.result())
        pool.submit(distance_guesser, frame, faceDetection.result())

    LeftLookingDetection, RightLookingDetection = profile_reg_thread.result()
    detection_drawing(frame, LeftLookingDetection, (0, 0, 255))
    detection_drawing(frame, RightLookingDetection, (200, 100, 200))

    fps = 1 / (new_frame_time - prev_frame_time)
    cv2.putText(frame, str(int(fps)), (7, 70), cv2.FONT_HERSHEY_PLAIN, 1, (100, 255, 0), 3, cv2.LINE_AA)
    cv2.imshow("Frame", frame)
    cv2.waitKey(1)
# do a bit of cleanup
# cv2.destroyAllWindows()
# fvs.stop()
