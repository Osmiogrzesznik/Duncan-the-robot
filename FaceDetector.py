'''
Face Detector needs to generate timestamp at when face was detected,
This allows for logic such as determining whether there are two
 persons or one, how many people are in the room for FaceRecognizer

 Face cascade returns list of face positions
 timestamp will be generated per frame
'''
import cv2


class FaceDetector:

    def __init__(self, path_to_cascade_classifier):
        self.path_to_cascade_classifier = path_to_cascade_classifier
