import cv2

stop_threads = False
requestFeed = False
referencePhoto = None
currentPhoto = None
webcam = cv2.VideoCapture(0)
pixel = [320, 240]
encounters = 0
encounterFound = False
sensorVal = 0
ser = None
vid = None