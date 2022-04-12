
# Personel Cameras

This project aims to bring smart cameras to users homes without
relying on a large company for their cloud or APis, the main 
smart features  are **face detection**, **person detection** and **movement detection**
and then using servos attached to the **raspberry pi** powered camera,
move and follow thease detections. with additional features such as 
**SMS** alerts **discord** alerts via webhook





## Usage/Examples
Most features can be run on eather the camera or the server depending on the processing power
of your avaliable devices. The settings can be turned on and off in the Manage Cameras section
where it will let you see all the options.
### Face detection
**note: this is Detection not regocnition cant tell people apart**
![App Screenshot](https://drive.google.com/uc?export=view&id=1UMOz-CGtp28YasqUECdHYgDwQLMUX2p1)
```python
def face_recognizer(grey_img):
    """
    function that returns the x and y of the face on the image and the width and height of the face
    uses a haarcascade xml file to guess the faces.
    note: only recognises faces from front on.
    """
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faces: list = face_cascade.detectMultiScale(grey_img, scaleFactor=1.15, minNeighbors=13)
    return faces
```

### Distance Guessing
**note: face detection will need to be turned on aswell**
guesses a persons distance from the camera based off the size of their face 
![App Screenshot](https://drive.google.com/uc?export=view&id=10nxmDOIX3egi_qLDYOP6D3RVMjUVOqCo)
```python
def distance_guesser(img, face_detections):
    """
    guesses the distance of a persons face by measuring their face size and comparing it to average detected face size
    :param img: the frame being used
    :param face_detections: where the detections are located
    :return: adds text to the images
    """
    contact = []
    for x, y, w, h in face_detections:
        imgHeight, imgWidth, ignore = img.shape
        distance = (16 * imgWidth) / w  # 655.6
        contact.append([float(distance), float(x + (0.5 * w)), float(y + (0.5 * h))])

        cv2.putText(img, f'{distance} CM', (x + 12, y - 13), cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                    (0, 0, 0), 2)
```

### profile recognizer
**note: Two seprate detections for looking left/ Right**
guesses a persons distance from the camera based off the size of their face 
![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)
```python
def profile_recognizer(grey_img):
    """
    detects the sides of the faces only recognizes looking one way so image is reverse and
    detections ran again to detect facing other way
    :param grey_img: takes in the grey scale version of the image
    :return: any detections
    """
    face_cascade = cv2.CascadeClassifier("haarcascade_profileface.xml")
    LeftLooking = face_cascade.detectMultiScale(grey_img, scaleFactor=1.15, minNeighbors=9)
    flipped = cv2.flip(grey_img, 1)
    RightLooking = face_cascade.detectMultiScale(flipped, scaleFactor=1.15, minNeighbors=9)
    for detection in range(len(RightLooking)):
        height, width = grey_img.shape
        RightLooking[detection][0] = width - RightLooking[detection][0] - RightLooking[detection][2]

    return LeftLooking, RightLooking

```

### Movement detection
**note: Needs two grey scale frames to compare for movement**
Using two seprate images it compares for changes in colour/shade and then if the change is over a certain amount then it will return a movement detection.
![App Screenshot](https://drive.google.com/uc?export=view&id=1Fi1AI2qKxJnAeNXMVo85CjfS2jfObx8t)
```python
def movement_detection(last_img, grey_img, img, Draw_boxes=False, colour=(0, 200, 0)):
    """
    detects movement from the camera and reports it back
    """
    movement_detected = False
    # smooths the image to make it so that differences are slightly larger and smaller contours
    # do not have to be processed
    blurredGray = cv2.GaussianBlur(grey_img, (21, 21), 0)
    # the delta frame will tell the colour difference between the old frame and the new frame,
    # as it is grey scale this will be a single number
    delta_frame = cv2.absdiff(blurredGray, last_img)
    # threshold will turn any difference number above a certain amount into white rest will be black
    thresh_frame = cv2.threshold(delta_frame, 55, 255, cv2.THRESH_BINARY)[1]
    # makes the white areas slightly larger this will connect areas of moving objects making detection better
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
    first_frame = blurredGray

    # uncomment too see detection clearer
    # cv2.imshow("Threshold Frame", thresh_frame)
    (contours, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    imgHeight, imgWidth = grey_img.shape
    totalPix = imgHeight * imgWidth
    for contour in contours:
        # only show contours bigger then a certain size to get rid of any small differences (such as a leaf moving)
        if cv2.contourArea(contour) > (totalPix * 0.007):
            movement_detected = True
            if Draw_boxes:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), colour, 1)
    return movement_detected

```


### Posting to Discord
**note: Needs two grey scale frames to compare for movement**
Using two seprate images it compares for changes in colour/shade and then if the change is over a certain amount then it will return a movement detection.
![App Screenshot](https://drive.google.com/uc?export=view&id=1nm0GrOuy9ZPKcB3w2BcV8NSNDO5SXCZh)
```python
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

```



## Installation

Install The project from downloading git

```bash
  git clone <<link here>>
```

Then you will want to go into the project and install the 
correct python libarys

### Method 1
use the requirements.txt, terminal
 into the base folder and run the following command
```bash 
pip install -r requirements.txt
```

### Method 2
Manually download libarys, install the libarys however you wish i will
list the libary and versions here:

| Libary | version |
|:-----|:--------:|
| Django | `3.2.8` |
| opencv-python   |  `4.5.3.56`  |
| pandas   | `1.3.4` |
| numpy  | `2.26.0` |
| requests   | `2.26.0` |
| discordwebhook  | `1.0.2` |

example of how to intall libary using pip

```bash 
pip install <<libary here>>==<<version>>
```

### Known issues
openCV can be difficuly to intall on a raspberry pi using pip.
This is due to it not automatically installing all dependicies.
example of how to do this [Here](https://tutorials-raspberrypi.com/installing-opencv-on-the-raspberry-pi/)
## Deployment

**Note: follow steps in installation first**

To Run one of the cameras

```bash
  python3 py-CamSystem.py
```

To deploy this project run the following command in the CamSystem
folder.

```bash
  python manage.py runserver
```

### Run on start up/ in background

I will cover how to run this as a service in linux using sytemMD
make the following file:
```bash
/etc/systemd/system/<< servicename >>.service
```
Add the following to the file:

------------


\[Unit\]<br />Description=My test service <br /> After=multi-user.target 

[Service]<br />Type=simple<br />Restart=always<br />ExecStart=/usr/bin/python3 /home/<username>/test.py

[Install]<br />WantedBy=multi-user.target 

------------

refresh the system control to see the new service

```bash
sudo systemctl enable << servicename >>.service
```

enable the service

```bash
sudo systemctl start << servicename >>.service
```


## Environment Variables

Django has a built in secret key you should do into this folder and edit it
the folder is located in:
```bash
/Camsystem/Camsystem/settings.py 
```


