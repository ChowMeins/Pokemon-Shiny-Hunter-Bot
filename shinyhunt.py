# This program is a simple program to test that the arduino is properly connected to the program.
import serial
import time
import cv2
import keyboard
import threading
import numpy as np
import os

stop_threads = False
requestFeed = False
referencePhoto = None
currentPhoto = None
webcam = cv2.VideoCapture(0)
pixel = [320, 240]
resets = 0

# Read's User's Input to determine what pixels to read
def determinePixel(pixel):
    if keyboard.is_pressed('w'):
        pixel[0] -= 1
    elif keyboard.is_pressed('s'):
        pixel[0] += 1
    elif keyboard.is_pressed('a'):
        pixel[1] -= 1
    elif keyboard.is_pressed('d'):
        pixel[1] += 1

# Creates the red border around the users pixel to read
def colorPixel(pixel, frame):
    # Creates a hxw red dot for the user to control, ignoring the center pixel
    borderHeight = 11
    borderWidth = 15
    for i in range(borderHeight):
        frame[pixel[0] - int(borderHeight / 2) + i, pixel[1] - int(borderWidth / 2)] = [0, 0, 255]
        frame[pixel[0] - int(borderHeight / 2) + i, pixel[1] + int(borderWidth / 2)] = [0, 0, 255]
        for j in range(borderWidth):
            if(i == 0 or i == borderHeight - 1):
                frame[pixel[0] - int(borderHeight / 2) + i, pixel[1] - int(borderWidth / 2) + j] = [0, 0, 255]

# Takes the average of all RGB values within the user's border
def findThresholdExceededCount(pixel, frame):
    global referencePhoto

    areaHeight = 9
    areaWidth = 13
    RGBthreshold = 20
    numThresholdExceeded = 0
    for i in range(areaHeight):
        for j in range(areaWidth):
            currPixelRGBValues = frame[pixel[0] - int(areaHeight / 2) + i, pixel[1] - int(areaWidth / 2) + j].astype('int32')
            referencePixelRGBValues = referencePhoto[pixel[0] - int(areaHeight / 2) + i, pixel[1] - int(areaWidth / 2) + j].astype('int32')
            pixelDiffs = abs(currPixelRGBValues - referencePixelRGBValues)
            #print("Current:", currPixelRGBValues, ", Original:", referencePixelRGBValues, ", Difference: ", pixelDiffs)
            if (pixelDiffs[2] >= RGBthreshold or pixelDiffs[1] >= RGBthreshold or pixelDiffs[0] >= RGBthreshold):
                numThresholdExceeded += 1
    return numThresholdExceeded

# Sends commands to arduino
def sendCommand(ser, command, delay):
    time.sleep(delay)
    ser.write(bytes(command, 'UTF-8'))

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

def setInstructions():
    global stop_threads
    global referencePhoto
    global currentPhoto
    global requestFeed
    global pixel
    global resets
    global webcam
    threshold = 15

    while not stop_threads:
        # Start of reset and load into game
        sendCommand(ser, 'f', 0)
        sendCommand(ser, 'e', 1.5)
        sendCommand(ser, 'a', 11.5)
        sendCommand(ser, 'a', 1.25)
        sendCommand(ser, 'a', 2)
        sendCommand(ser, 'a', 3)

        # Loaded into game, talk to Bianca   
        sendCommand(ser, 'a', 6)
        sendCommand(ser, 'a', 1.25)
        sendCommand(ser, 'a', 0.75)
        sendCommand(ser, 'a', 0.75)
        sendCommand(ser, 'a', 0.75)

        # Select Tepig
        sendCommand(ser, 'a', 6.5)     
        sendCommand(ser, 'a', 0.75)
        sendCommand(ser, 'a', 0.75)

        # Receive Tepig
        sendCommand(ser, 'a', 9)        
        sendCommand(ser, 'a', 0.75)

        # Decline nickname option
        sendCommand(ser, 'b', 1.3)
        sendCommand(ser, 'a', 1)

        # Recieve Pokedex
        sendCommand(ser, 'a', 3.5)
        sendCommand(ser, 'a', 4.5)
        sendCommand(ser, 'a', 0.75)
        sendCommand(ser, 'a', 0.75)
        sendCommand(ser, 'a', 0.75)
        sendCommand(ser, 'a', 0.75)
        sendCommand(ser, 'a', 0.75)

        # Finish dialogue, open menu and select Tepig
        sendCommand(ser, 'x', 1.25)
        sendCommand(ser, 'a', 1.5)
        sendCommand(ser, 'a', 1.5)
        sendCommand(ser, 'a', 1)

        time.sleep(2) # Wait for starter pokemon to be visible
        requestFeed(webcam)
        # Read RGB values
        # On first reset, determine which pixel to read
        if (resets == 0):
            while(vid.isOpened()):
                if (referencePhoto is not None):
                    currImg = np.copy(referencePhoto)
                    determinePixel(pixel)
                    colorPixel(pixel, currImg)
                    cv2.imshow('Reference Photo', currImg)
                    if cv2.waitKey(1) & 0xFF == ord('x'):
                        cv2.destroyWindow('Reference Photo')
                        cv2.imwrite('referencePhoto.jpg', currImg)
                        break
        if(cv2.getWindowProperty('Reference Photo', cv2.WND_PROP_VISIBLE) != 1):
            colorPixel(pixel, currentPhoto)
            cv2.imwrite('currentPhoto.jpg', currentPhoto)
            cv2.imwrite('./encounters/encounter' + str(resets) + '.jpg', currentPhoto)
            pixelExceededCount = findThresholdExceededCount(pixel, currentPhoto)
            print("Resets:", resets, ", # of pixels exceeding threshold:", pixelExceededCount)
            if (pixelExceededCount > threshold):
                found = input("Pixel count threshold exceeded. Is this a shiny? (y/n) ")
                if (found.lower() == 'y'):
                    break
                elif (found.lower() == 'n'):
                    referencePhoto = np.copy(currentPhoto)
                    cv2.imwrite('referencePhoto.jpg', referencePhoto)
        resets += 1

if __name__ == '__main__':
    # Connect to Arduino
    ser = serial.Serial(port='COM3', baudrate=9600, timeout=5)
    print("Connected to", ser.name)
    time.sleep(2)

    # Connect to Webcam
    vid = cv2.VideoCapture(0)

    # Remove every photo in directory
    #path = './encounters'
    #dir = os.listdir(path)
    #for file in dir:
    #    os.remove(path + '/' + file)
    t1 = threading.Thread(target=record)
    t2 = threading.Thread(target=setInstructions)
    t2.daemon = True

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("Program terminating...")
    # Close all windows
    vid.release()
    cv2.destroyAllWindows()
