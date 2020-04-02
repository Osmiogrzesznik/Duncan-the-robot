"""
   *Face Tracking System Using Arduino - Python Code*
    Close the Arduino IDE before running this code to avoid Serial conflicts.
    Replace 'COM5' with the name of port where you arduino is connected.
    To find the port check Arduino IDE >> Tools >> port.
    Upload the Arduino code before executing this code.

    # Code by Harsh Dethe, 09 Sep 2018 #
"""
import numpy as np
import serial
import time
import io
import sys
import cv2
import subprocess


def hello():
    print("hello")
    subprocess.run(
        ["play", "2020-04-01_16-07-12_749_googtts.mp3", "pitch", "500"])


def sayInit():
    print("initialising")
    subprocess.run(
        ["play", "2020-04-01_16-04-11_233_googtts.mp3", "pitch", "500"])


arduino = serial.Serial('/dev/ttyUSB0', 9600)
time.sleep(2)
print("Connection to arduino...")
print(arduino.name)
sio = io.TextIOWrapper(io.BufferedRWPair(arduino, arduino))
arduino.timeout = 1
pth = "/home/pi/.local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_alt_tree.xml"

face_cascade = cv2.CascadeClassifier(pth)

cap = cv2.VideoCapture(0)
sayInit()

while 1:
    ret, img = cap.read()
    # cv2.resizeWindow('img', 500,500)
    # cv2.line(img,(500,250),(0,250),(0,255,0),1)
    # cv2.line(img,(250,0),(250,500),(0,255,0),1)
    # cv2.circle(img, (250, 250), 5, (255, 255, 255), -1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3)

    for (x, y, w, h) in faces:

        # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),5)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

        arr = {y: y+h, x: x+w}
        print(arr)

        print('X :' + str(x))
        print('Y :'+str(y))
        print('x+w :' + str(x+w))
        print('y+h :' + str(y+h))

        xx = int(x+(x+h))/2
        yy = int(y+(y+w))/2

        # zapamietaj xx yy i jesli byly wieksze od center
        # zeby obracal sie jak twarz zniknie z pola widzenia
        # popen hello, human

        print(xx)
        print(yy)

        center = (xx, yy)

        print("Center of Rectangle is :", center)
        data = "d={0:.0f} p0 m:n0  m0n:  m:n0  m0n:  m5n5 p0".format(xx)
        # data = "d={0:.0f} l={2:.0f} r={3:.0f} m={2:.0f} n={3:.0f} ".format(xx, yy, xx/2, yy/2)
        print("output = '" + data + "'")
        hello()
        sio.write(data)
        sio.flush()
        print(sio.readlines())

        # arduino.write(data)

    # cv2.imshow('img',img)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
