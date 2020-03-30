import serial
import io
import subprocess

ser = serial.Serial('/dev/ttyUSB0')
print ser.name
sio = io.TextIOWrapper(io.BufferedRWPair(ser,ser))
ser.timeout = 1;
sio.flush()
sio.write(unicode("p: l2d: p:p: l6 d0 l2 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 p: \n"))
sio.flush()
subprocess = subprocess.Popen("espeak \"Hey\" --stdout | aplay",True)
sio.write(unicode("p: l2d: p:p: l6 d0 l2 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 p: \n"))
sio.flush()
sio.write(unicode("p: l2d: p:p: l6 d0 l2 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 p: \n"))
sio.flush()


