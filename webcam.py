import cv2
from globals import stop_threads, requestFeed, referencePhoto, currentPhoto, webcam, pixel, resets, sensorVal

# Shows live webcam feed
def record():
    global stop_threads
    global requestFeed
    global webcam

    while not stop_threads:
        if (webcam.isOpened()):
            ret, frame = webcam.read()
            cv2.imshow("Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                stop_threads = True
                webcam.release()
                cv2.destroyAllWindows()
                break

# Reads the webcam to initialize/declare the variables currentPhoto and referencePhoto
def requestFeed(webcam):
    global referencePhoto
    global currentPhoto

    if (webcam.isOpened()):
        ret, frame = webcam.read()
        currentPhoto = frame
        if (referencePhoto is None):
            referencePhoto = frame