# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import cv2
import serial
import io
import subprocess
from os import name as osname

WINDOWS = False
LINUX = False
print(osname)
WINDOWS = osname == "nt"
LINUX = osname == "posix"

# if WINDOWS:
#     subprocess.run(["Add-Type", "-AssemblyName", "System.speech"])
# subprocess.run(
# "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer")


def hello():
    print("hello")
    if LINUX:
        # subprocess.run(
        #     ["play", "2020-04-01_16-07-12_749_googtts.mp3", "pitch", "500"])
        subprocess.Popen(
            ["play", "2020-04-01_16-07-12_749_googtts.mp3", "pitch", "500"])


def sayInit():
    print("initialising")
    if LINUX:
        # subprocess.run(
        #     ["play", "2020-04-01_16-04-11_233_googtts.mp3", "pitch", "500"])
        subprocess.Popen(
            ["play", "2020-04-01_16-04-11_233_googtts.mp3", "pitch", "500"])


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)
if WINDOWS:
    pathToCascadeClassifier = "haarcascade_frontalface_alt_tree.xml"
    serialport = 'COM6'
else:
    pathToCascadeClassifier = "/home/pi/.local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_alt_tree.xml"
    serialport = '/dev/ttyUSB0'
try:
    arduino = serial.Serial(serialport, 9600)
    arduino.timeout = 1
    print(arduino.name)
    sio = io.TextIOWrapper(io.BufferedRWPair(arduino, arduino))
except:
    print("______________NO ARDUINO FOUND!!!!!")
    sio = io.TextIOWrapper(io.BufferedRWPair(
        io.FileIO("bubuin.txt"), io.FileIO("bubuout.txt", mode='w')))


print(sio.readlines())
sayInit()
face_cascade = cv2.CascadeClassifier(pathToCascadeClassifier)

# initialize the video stream and allow the camera sensor to
# warmup
# vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
# time.sleep(2.0)


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


def detect_face(frameCount):
    lastx = None
    lasty = None
    lastw = None
    lasth = None
    # grab global references to the video stream, output frame, and lock
    global vs, outputFrame, lock, face_cascade
    face_was_just_detected = False
    count = 0
    count_since_detection = 0
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # here do not detect if face was just detected, only draw the same rectangle over frames
        # do this only if time from detection framcount has passed
        if (face_was_just_detected):
            # dont send any signals to arduino if face was detected just moment ago (defined by frameCount)
            if count_since_detection > frameCount:
                face_was_just_detected = False
            else:
                count_since_detection += 1
                cv2.rectangle(frame, (lastx, lasty),
                              (lastx+lastw, lasty+lasth), (30, 100, 30), 5)

        else:  # try to detect face and if detected - send to arduino
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3)
            for (x, y, w, h) in faces:

                # this mechanism blocks detecting more than one face simultaneously
                lastx = x
                lasty = y
                lastw = w
                lasth = h
                count_since_detection = 0
                face_was_just_detected = True
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 5)
                xx = int(x+(x+h))/2
                yy = int(y+(y+w))/2
                arr = {x: xx, y: yy}
                print(arr)
                data = "d={0:.0f} p0 m:n0  m0n:  m:n0  m0n:  m5n5 p0".format(
                    xx)
                # data = "d={0:.0f} l={2:.0f} r={3:.0f} m={2:.0f} n={3:.0f} ".format(xx, yy, xx/2, yy/2)
                print("output = '" + data + "'")
                sio.write(data)
                sio.flush()
                print(sio.readlines())
                hello()  # TODO comment this out and see if affects stutter
            # timestamp = datetime.datetime.now()
            # cv2.putText(frame, timestamp.strftime(
            #     "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
            #     cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # acquire the lock, set the output frame, and release the
            # lock
        with lock:
            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=320,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # start a thread that will perform motion detection
    t = threading.Thread(target=detect_face, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()
