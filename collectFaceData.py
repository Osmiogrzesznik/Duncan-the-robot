"""
This script supposed to run on Windows machine to collect face data for training
"""
from imutils.video import VideoStream
import imutils
import cv2
from os import name as osname

WINDOWS = False
LINUX = False
print(osname)
WINDOWS = osname == "nt"
LINUX = osname == "posix"
PATH_TO_FACES_DATA_IMAGES = "C:\\Users\\" + \
    # change this line to point to your project
"absolute\\path\\to\\your\\windows\\folder" + \
    "\\facesData\\User."


id = input("give person id")
HOWMANYPICTURES = input("how many pictures to collect")


def hello():
    print("hello")


def sayInit():
    print("initialising")


if WINDOWS:
    pathToCascadeClassifier = "haarcascade_frontalface_alt_tree.xml"
else:
    pathToCascadeClassifier = "/home/pi/.local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_alt_tree.xml"

sayInit()
face_cascade = cv2.CascadeClassifier(pathToCascadeClassifier)

# initialize the video stream and allow the camera sensor to
# warmup
# vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
# time.sleep(2.0)


def detect_face(frameCount):

    # grab global references to the video stream, output frame, and lock
    global vs, outputFrame, lock, face_cascade, id
    trainSampleN = 0
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # here do not detect if face was just detected, only draw the same rectangle over frames
        # do this only if time from detection framcount has passed

        else:  # try to detect face and if detected - send to arduino
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3)
            for (x, y, w, h) in faces:
                trainSampleN += 1
                # save detected face for learning
                if not cv2.imwrite(PATH_TO_FACES_DATA_IMAGES + str(id) + "." + str(trainSampleN) + ".jpg", gray[y:y+h, x:x+w]):
                    raise Exception("Could not write image")

        if trainSampleN > HOWMANYPICTURES:
            print("finished!")
            break

