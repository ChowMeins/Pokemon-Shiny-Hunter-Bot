import cv2
import globals as g
# Shows live webcam feed
def record():
    while not g.stop_threads:
        if (g.webcam.isOpened()):
            ret, frame = g.webcam.read()
            cv2.imshow("Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                g.stop_threads = True
                g.webcam.release()
                cv2.destroyAllWindows()
                break

# Reads the webcam to initialize/declare the variables currentPhoto and referencePhoto
def requestFeed(webcam):
    if (webcam.isOpened()):
        ret, frame = webcam.read()
        g.currentPhoto = frame
        if (g.referencePhoto is None):
            g.referencePhoto = frame