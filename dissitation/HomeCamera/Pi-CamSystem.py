from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import cv2

from picamLib.APIConnection import post_to_api
from picamLib.PiCamera import PiCamera
from picamLib.ImageDetection import distance_guesser, profile_recognizer, movement_detection,\
    detection_drawing, face_recognizer

from HomeCamera.picamLib.APIConnection import post_to_discord_webhook

video = cv2.VideoCapture(0)

print("camera starting")
camera = PiCamera()
camera.ip = "172.17.144.1"
print(f"camera ip is: {camera.ip}")
print(f"attempting to connect to host on localhost:8000")
camera.collect_settings()
if camera.error == "":
    print("connected")
else:
    print("connection failed")
camera.update()
last_gray = cv2.cvtColor(camera.frame, cv2.COLOR_BGR2GRAY)
Detection = False
while not camera.stopped:
    gray = cv2.cvtColor(camera.frame, cv2.COLOR_BGR2GRAY)
    with ThreadPoolExecutor(max_workers=2) as pool:
        if camera.settings["face_detection"] == "CAMERA":
            faceDetection = pool.submit(face_recognizer, gray)
            if faceDetection.result():
                Detection = True
            pool.submit(detection_drawing, camera.frame, faceDetection.result())
            if camera.settings["distance_guesser"] == "CAMERA":
                pool.submit(distance_guesser, camera.frame, faceDetection.result())
        if camera.settings["profile_detection"] == "CAMERA":
            profile_reg_thread = pool.submit(profile_recognizer, gray)
        if camera.settings["movement_detection"] == "CAMERA":
            pool.submit(movement_detection, last_gray, gray, camera.frame, True)

    if camera.settings["profile_detection"] == "CAMERA":
        LeftLookingDetection, RightLookingDetection = profile_reg_thread.result()
        detection_drawing(camera.frame, LeftLookingDetection, (0, 0, 255))
        detection_drawing(camera.frame, RightLookingDetection, (200, 100, 200))
    if camera.settings["fps"]:
        cv2.putText(camera.frame, str(int(camera.fps())), (7, 70), cv2.FONT_HERSHEY_PLAIN, 3, (100, 255, 0), 3,
                    cv2.LINE_AA)

    #cv2.imshow("Color Frame", camera.frame)
    post_to_api(camera.frame, camera.ip)
    if Detection:
        if camera.settings["discord_webhook"] != "unknown":
            try:
                post_to_discord_webhook(camera.frame, camera.settings["discord_webhook"], "living room")
            except:
                print("discord webhook not working")
    Detection = False
    key = cv2.waitKey(1)
    camera.update()
    last_gray = gray
    # if key == ord('q'):
    #    break


video.release()
# if face_detected is True and movement_detected is True:
# result.release()

cv2.destroyAllWindows()
