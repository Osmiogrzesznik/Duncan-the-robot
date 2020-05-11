import pyttsx3

tts = pyttsx3.init()

for i in range(0, 5):
    tts.say(i)
    tts.runAndWait()
