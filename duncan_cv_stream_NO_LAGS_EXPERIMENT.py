# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
import Person
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from flask import jsonify
from flask_socketio import SocketIO, send, emit
import threading
import argparse
import imutils
import cv2
import serial
import io
import subprocess
from os import name as osname
from os import path as ospath
from os import listdir as oslistdir
VERBOSITY = 1
DEBUGLEVEL = 1
CAPTURE_NEW_IMAGES = True
VIDEO_FRAME_WIDTH = 400
PLAY_GAME = False
limb_positions = {
    "l": 90,
    "r": 90,
    "m": 90,
    "n": 90,
    "d": 90
}
limb_increments = {
    "l": 2,
    "r": 2,
    "m": 2,
    "n": 2,
    "d": 2
}


def logD(msg):
    if VERBOSITY >= DEBUGLEVEL:
        print(msg)


WINDOWS = False
LINUX = False
logD(osname)
WINDOWS = osname == "nt"
LINUX = osname == "posix"

if WINDOWS:
    import pyttsx3
    tts = pyttsx3.init()
    tts.say("initialising on windows")
    tts.runAndWait()


recognizer = cv2.face.LBPHFaceRecognizer_create()

persons = ["Human", "Bolek", "Maciek", "Ania"]
personsPico = ["Human", "Bolek", "Maciek", "Ania"]
greetings = ["hello.mp3", "bolek.mp3", "maciek.mp3", "ania.mp3"]
# if WINDOWS:
#     subprocess.run(["Add-Type", "-AssemblyName", "System.speech"])
# subprocess.run(
# "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer")
gameproc = None


def playGame(face_id):
    hello(face_id)
    global gameproc, PLAY_GAME
    if not PLAY_GAME:
        return
    if WINDOWS:
        logD("------------no game on WINDOWS YET")
        return
    # if game was not played or finished and returned 0,:
    if gameproc == None or gameproc.poll() == 0:
        gameproc = subprocess.Popen([
            "python3",
            "/home/pi/duncanStream/animal-guesser/guesser.py"
        ])
    else:
        logD("--------------------we did not finished playing yet or there was an error")


def printsay(msg):
    # TODO these if's are ugly speech_wrapper should be used to provide abstraction
    # tts should be accessed from thread that initialised it (to prevent the problem with blocked tts in pure python)
    #
    #
    #
    #

    if WINDOWS:
        global tts
        logD("saying:" + msg)
        tts.say(msg)
        tts.runAndWait()
        logD("said:{}".format(msg))
        logD(tts.isBusy())
        if not tts.isBusy():
            tts.runAndWait()
        return
    # record a utterance
    p = subprocess.Popen([
        "pico2wave",
        "-w",
        "pico.wav",
        "-l",
        "en-GB",
        msg
    ])
    retcode = p.wait()
    if retcode == 0:
        # play utterance
        p2 = subprocess.Popen(
            ["play", "pico.wav", "pitch", "300"])
        retcode = p2.wait()
        if retcode == 0:
            logD(msg)
            return
    else:
        logD("some error:" + str(retcode))


def hello(face_id):
    # TODO if class was to be used for whole greetings persons
    #   then i would get rid of globals
    #
    #
    #
    global greetings, persons, personsPico
    logD("hello" + persons[face_id])
    printsay("hello" + personsPico[face_id])


def do_Move(msg):
    global sio
    data = msg
    # data = "d={0:.0f} l={2:.0f} r={3:.0f} m={2:.0f} n={3:.0f} ".format(xx, yy, xx/2, yy/2)
    logD("output = '" + data + "'")
    sio.write(data)
    sio.flush()
    # logD(sio.readlines())


def beHappy():
    return
    global sio
    data = "l:r0 p3 l0r: p3 l:r0 p3 l0r: p3 l5r5 p0"
    # data = "d={0:.0f} l={2:.0f} r={3:.0f} m={2:.0f} n={3:.0f} ".format(xx, yy, xx/2, yy/2)
    do_Move(data)


def beSad():
    return
    global sio
    data = "l:r0 p9 l0r: p9 l5r5 p0"
    # data = "d={0:.0f} l={2:.0f} r={3:.0f} m={2:.0f} n={3:.0f} ".format(xx, yy, xx/2, yy/2)
    do_Move(data)


def moveTowardFace(xx):
    logD("moving toward face")
    global sio
    data = "d={0:.0f} p0".format(
        xx)
    # data = "d={0:.0f} l={2:.0f} r={3:.0f} m={2:.0f} n={3:.0f} ".format(xx, yy, xx/2, yy/2)
    do_Move(data)


def getPositionsFromArduino():
    global limb_positions, sio
    do_Move("*")
    StrList = sio.readlines()
    print(StrList)
    return jsonify(StrList)


def saveimage(face_id, trainSampleN, img_arr):
    if not CAPTURE_NEW_IMAGES:
        return trainSampleN
    if not cv2.imwrite(FACESDATA_PATH + "User."+str(face_id) + "." + str(trainSampleN) + ".jpg", img_arr):
        raise Exception("Could not write image")
    else:
        trainSampleN += 1
    return trainSampleN


def sayInit():
    logD("initialising")
    printsay("initialising all systems")
    # subprocess.run(
    #     ["play", "2020-04-01_16-04-11_233_googtts.mp3", "pitch", "500"])
    # subprocess.Popen(
    #     ["play", "2020-04-01_16-04-11_233_googtts.mp3", "pitch", "500"])


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)
socketio = SocketIO(app)

# TODO make two folders : WINDOWS and LINUX to easier update github repository
if WINDOWS:
    FACESDATA_PATH = "C:\\Users\\boles\\OneDrive\\Desktop\\MOJE_PROJEKTY\\Arduino\\dunc_zaczepia\\facesData\\"
    pathToCascadeClassifier = "haarcascade_frontalface_alt_tree.xml"
    serialport = 'COM6'
    recognizer.read(
        "C:\\Users\\boles\\OneDrive\\Desktop\\MOJE_PROJEKTY\\Arduino\\dunc_zaczepia\\face_rec\\face_rec_BOL_MAC_ANA.yml")

else:
    FACESDATA_PATH = "/home/pi/duncanStream/facesData/"
    pathToCascadeClassifier = "/home/pi/.local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_alt_tree.xml"
    serialport = '/dev/ttyUSB0'
    recognizer.read(
        "face_rec.yml")

try:
    arduino = serial.Serial(serialport, 9600)
    arduino.timeout = 1
    logD(arduino.name)
    sio = io.TextIOWrapper(io.BufferedRWPair(arduino, arduino))
except:

    logD("______________NO ARDUINO FOUND!!!!!")
    input("arduino not found - text will be send to dummy file instead of arduino serila port")
    sio = io.TextIOWrapper(io.BufferedRWPair(
        io.FileIO("bubuin.txt"), io.FileIO("bubuout.txt", mode='w')))


logD(sio.readlines())
sayInit()

face_cascade = cv2.CascadeClassifier(pathToCascadeClassifier)

# initialize the video stream and allow the camera sensor to
# warmup
# vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
# time.sleep(2.0)


@socketio.on('program', namespace='/duncanws')
def ws_program(message):
    global sio
    print('Message: ' + message['data'])
    do_Move(message['data'])
    emit('positions', {'data': sio.read()})


@socketio.on('connect', namespace='/duncanws')
def ws_connect():
    global sio
    print('Client connected')
    emit('positions', {'data': sio.read()})


@socketio.on('py', namespace='/duncanws')
def ws_cmd(message):
    print('command:', message['cmd'])
    print('data:', message['data'])
    c = message.cmd
    # TODO do something with received command
    emit('py rsp', {data: 'ok'})


@socketio.on('say', namespace='/duncanws')
def ws_say(message):
    print(message['data'])
    printsay(message['data'])
    emit('py rsp', {data: 'ok'})


@socketio.on('disconnect', namespace='/duncanws')
def ws_disconnect():
    print('Client disconnected')


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


def main_loop_function_to_be_run_in_separate_thread(frameCount):
    lastx = None
    lasty = None
    lastw = None
    lasth = None
    lastlabel = None
    # grab global references to the video stream, output frame, and lock
    global vs, outputFrame, lock, face_cascade, recognizer, persons, gameproc, VIDEO_FRAME_WIDTH
    face_was_just_detected = False
    count = 0
    count_since_detection = 0
    new_face_id = len(persons)
    # simple version for working with CWD
    trainSampleN = len(
        [fnm for fnm in oslistdir('.') if ospath.isfile(fnm)])
    do_Move("v")  # turn of serial debuggin (faster reaction )
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=VIDEO_FRAME_WIDTH)
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
                cv2.putText(frame, lastlabel, (lastx, lasty+lasth),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

        else:  # try to detect face and if detected - send to arduino
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3)
            for (x, y, w, h) in faces:
                # TODO
                # First iterate over all faces identyfying each, set persons new positions
                # and then try to do different things depending on amount of faces
                # each person should have its own face_was_just_detected, count_since_detection (based on timestamps rather than else)
                # each loop check if person dissapeared for more than some time to avoid keeping saying hello
                # if new person appears duncan may say sorry B i am currently playing with A
                # and turn to each person in some other mode where multiplayer is possible
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                #
                # this mechanism blocks detecting more than one face simultaneously
                lastx = x
                lasty = y
                lastw = w
                lasth = h
                # predict who is on the picture
                face_id, confusion = recognizer.predict(gray[y:y+h, x:x+w])
                if (confusion > 120):
                    face_id = 0

                confusion = "U{0:.0f}".format(confusion)
                name = persons[face_id]
                label = str(name + "\n" + str(confusion))
                logD(label)
                lastlabel = label
                count_since_detection = 0
                face_was_just_detected = True
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 5)
                cv2.putText(frame, label, (x, y+h),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

                xx = int(x+(x+h))/2
                yy = int(y+(y+w))/2
                arr = {x: xx, y: yy}
                logD(arr)
                do_Move("d={0:.0f}".format(xx))
                if gameproc == None:
                    hello(face_id)
                    # moveTowardFace(xx)
                    # TODO comment this out and see if affects stutter. May need polling for a process
                    # hello(face_id)
                    if face_id > 0:
                        beHappy()
                        hello(face_id)
                        trainSampleN = saveimage(
                            face_id, trainSampleN, gray[y:y+h, x:x+w])
                        playGame(face_id)
                    else:  # dont know the person
                        trainSampleN = saveimage(
                            new_face_id, trainSampleN, gray[y:y+h, x:x+w])
                        beSad()
                        printsay(
                            "sorry, i dont know you yet")

                else:  # game has started at least once
                    logD(gameproc.poll())
                    # moveTowardFace(xx)
                    if gameproc.poll() == 0:  # if game finished and returned 0 (okay)
                        if face_id > 0:  # and he recognized person
                            # moveTowardFace(xx)
                            hello(face_id)
                            playGame(face_id)
                        else:  # if game finished and returned 0, but he didnt recognized person
                            # moveTowardFace(xx)
                            hello(face_id)
                            printsay(
                                "sorry, human but i dont recognize you, and i do not play with strangers.")
                    elif gameproc.poll() == None:  # if game goes on
                        do_Move()

                        # or there was an error in game
                        # TODO refactor if statements

            # timestamp = datetime.datetime.now()
            # cv2.putText(frame, timestamp.strftime(
            #     "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
            #     cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # acquire the lock, set the output frame, and release the
            # lock
            # TODO good idea to extract movement module to make duncan be happy whenever he guesses correctly
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
    return Response(generateVideoFrame(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--frame-count", type=int, default=320,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # start face detection loop in a new thread
    t = threading.Thread(target=main_loop_function_to_be_run_in_separate_thread, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()

    # start the socketio and associated flask app
    socketio.run(app, host='0.0.0.0', port=8080,
                 debug=True, use_reloader=False)

# release the video stream pointer
print("finished!!!!!!!!"*99999)
vs.stop()
