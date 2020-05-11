"""
This script supposed to run on Windows machine to collect face data for training from scraped or prepared images folder
"""
import imutils
import cv2
import subprocess
import os
from PIL import Image

recognizer = cv2.face.LBPHFaceRecognizer_create()

id = input("give person id")
pathToCascadeClassifier = "haarcascade_frontalface_alt_tree.xml"
face_cascade = cv2.CascadeClassifier(pathToCascadeClassifier)
path = "C:\\Users\\boles\\OneDrive\\Desktop\\MOJE_PROJEKTY\\Arduino\\dunc_zaczepia\\facesData2"  # input

# vs = VideoStream(src=0).start()
imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
# grab global references to the video stream, output frame, and lock
trainSampleN = 21
for imagePath in imagePaths:
    frame = cv2.imread(imagePath)
    # here do not detect if face was just detected, only draw the same rectangle over frames
    # do this only if time from detection framcount has passed
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # input(imagePath)
    faces = face_cascade.detectMultiScale(gray, 1.3)
    for (x, y, w, h) in faces:
        trainSampleN += 1
        # save detected face for learning
        if not cv2.imwrite("C:\\Users\\boles\\OneDrive\\Desktop\\MOJE_PROJEKTY\\Arduino\\dunc_zaczepia\\facesData\\User."+str(id) + "." + str(trainSampleN) + ".jpg", gray[y:y+h, x:x+w]):
            raise Exception("Could not write image")
        # this mechanism blocks detecting more than one face simultaneously
        #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 5)
        cv2.imshow(str(trainSampleN), gray[y:y+h, x:x+w])
        cv2.waitKey(10)

cv2.destroyAllWindows()
