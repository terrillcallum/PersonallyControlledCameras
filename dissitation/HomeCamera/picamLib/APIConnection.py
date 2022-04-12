import base64
from datetime import datetime

import cv2
import requests
from discordwebhook import Discord


def post_to_api(img, ip_address):
    """
    this posts up the image that was taken to the webserver
    the image is turned into base64 then transmitted in a json dictionary format
    """
    # url = 'https://localhost:5001/Videostreaming/CameraRecording'
    url = 'http://127.0.0.1:8000/update_photo'  # camera_streams/'
    # url = 'http://jerboaworkshop.com/Videostreaming/CameraRecording'
    #url = 'http://192.168.1.94/update_photo'
    # scale_percent = 30  # percent of original size
    # width = int(img.shape[1] * scale_percent / 100)
    # height = int(img.shape[0] * scale_percent / 100)
    # dim = (width, height)

    # resize image
    # resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    image = cv2.imencode('.jpg', img)[1].tobytes()
    base64img = base64.b64encode(image)
    try:
        requests.post(url, data=dict(Photo=base64img, Device=ip_address), verify=False, timeout=0.1)
    except requests.exceptions.ReadTimeout:
        pass
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
                    "title": "Detection",
                    "description": "@everyone Camera has made a detection",
                    "fields": [
                        {"name": "Detection type", "value": "Face Detection", "inline": True},
                        {"name": "Time", "value": formatted_time, "inline": True},
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

