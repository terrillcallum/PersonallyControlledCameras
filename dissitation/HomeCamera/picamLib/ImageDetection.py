import cv2


def face_recognizer(grey_img):
    """
    function that returns the x and y of the face on the image and the width and height of the face
    uses a haarcascade xml file to guess the faces.
    note: only recognises faces from front on.
    """
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faces: list = face_cascade.detectMultiScale(grey_img, scaleFactor=1.15, minNeighbors=13)
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
