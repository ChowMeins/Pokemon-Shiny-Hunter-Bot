import cv2
import keyboard
import globals
import time
import numpy as np
import globals
from webcam import requestFeed

# Sends commands to arduino
def sendCommand(ser, command, delay):
    time.sleep(delay)
    ser.write(bytes(command, 'UTF-8'))
    print("Command sent")

def determinePixel(pixel):
    if keyboard.is_pressed('w'):
        pixel[0] -= 1
    elif keyboard.is_pressed('s'):
        pixel[0] += 1
    elif keyboard.is_pressed('a'):
        pixel[1] -= 1
    elif keyboard.is_pressed('d'):
        pixel[1] += 1

# Creates the red border around the uglobals.sers pixel to read
def colorPixel(pixel, frame):
    # Creates a hxw red dot for the uglobals.ser to control, ignoring the center pixel
    borderHeight = 11
    borderWidth = 15
    for i in range(borderHeight):
        frame[pixel[0] - int(borderHeight / 2) + i, pixel[1] - int(borderWidth / 2)] = [0, 0, 255]
        frame[pixel[0] - int(borderHeight / 2) + i, pixel[1] + int(borderWidth / 2)] = [0, 0, 255]
        for j in range(borderWidth):
            if(i == 0 or i == borderHeight - 1):
                frame[pixel[0] - int(borderHeight / 2) + i, pixel[1] - int(borderWidth / 2) + j] = [0, 0, 255]

# Takes the average of all RGB values within the uglobals.ser's border
def findThresholdExceededCount(pixel, frame):

    areaHeight = 9
    areaWidth = 13
    RGBthreshold = 20
    numThresholdExceeded = 0
    for i in range(areaHeight):
        for j in range(areaWidth):
            currPixelRGBValues = frame[pixel[0] - int(areaHeight / 2) + i, pixel[1] - int(areaWidth / 2) + j].astype('int32')
            referencePixelRGBValues = globals.referencePhoto[pixel[0] - int(areaHeight / 2) + i, pixel[1] - int(areaWidth / 2) + j].astype('int32')
            pixelDiffs = abs(currPixelRGBValues - referencePixelRGBValues)
            #print("Current:", currPixelRGBValues, ", Original:", referencePixelRGBValues, ", Difference: ", pixelDiffs)
            if (pixelDiffs[2] >= RGBthreshold or pixelDiffs[1] >= RGBthreshold or pixelDiffs[0] >= RGBthreshold):
                numThresholdExceeded += 1
    return numThresholdExceeded

def BW2Starter():
    threshold = 15
    starter = input("Select your Starter (enter a number):\n1.) Snivy\n2.) Tepig\n3. Oshawott\n")
    resets = 0

    while not globals.stop_threads:
        # Start of reset and load into game
        sendCommand(globals.ser, 'f\n', 1)
        sendCommand(globals.ser, 'e\n', 1.5)
        sendCommand(globals.ser, 'a\n', 10.5)
        sendCommand(globals.ser, 'a\n', 1.25)
        sendCommand(globals.ser, 'a\n', 2)
        sendCommand(globals.ser, 'a\n', 3)

        # Loaded into game, talk to Bianca   
        sendCommand(globals.ser, 'a\n', 5)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)

        # Select Tepig
        sendCommand(globals.ser, 'a\n', 6.5)    
        if (starter == "1"):
            sendCommand(globals.ser, 'l\n', 1.5)
        elif (starter == "3"):
            sendCommand(globals.ser, 'r\n', 1.5) 
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)

        # Receive Tepig
        sendCommand(globals.ser, 'a\n', 9)        
        sendCommand(globals.ser, 'a\n', 1.5)

        # Decline nickname option
        sendCommand(globals.ser, 'b\n', 1.5)
        sendCommand(globals.ser, 'a\n', 2)

        # Recieve Pokedex
        sendCommand(globals.ser, 'a\n', 3.5)
        sendCommand(globals.ser, 'a\n', 4.5)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)

        # Finish dialogue, open menu and select Tepig
        sendCommand(globals.ser, 'x\n', 1.25)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1.5)
        sendCommand(globals.ser, 'a\n', 1)

        time.sleep(6) # Wait for starter pokemon to be visible
        requestFeed(globals.webcam)
        # Read RGB values
        # On first reset, determine which pixel to read
        if (resets == 0):
            while(globals.webcam.isOpened()):
                if (globals.referencePhoto is not None):
                    currImg = np.copy(globals.referencePhoto)
                    determinePixel(globals.pixel)
                    colorPixel(globals.pixel, currImg)
                    cv2.imshow('Reference Photo', currImg)
                    if cv2.waitKey(1) & 0xFF == ord('x'):
                        cv2.destroyWindow('Reference Photo')
                        cv2.imwrite('referencePhoto.jpg', currImg)
                        break

        if(cv2.getWindowProperty('Reference Photo', cv2.WND_PROP_VISIBLE) != 1):
            colorPixel(globals.pixel, globals.currentPhoto)
            cv2.imwrite('currentPhoto.jpg', globals.currentPhoto)
            cv2.imwrite('./encounters/encounter' + str(resets) + '.jpg', globals.currentPhoto)
            pixelExceededCount = findThresholdExceededCount(globals.pixel, globals.currentPhoto)
            print("Resets:", resets, ", # of pixels exceeding threshold:", pixelExceededCount)
            if (pixelExceededCount > threshold):
                found = input("Pixel count threshold exceeded. Is this a shiny? (y/n) ")
                if (found.lower() == 'y'):
                    break
                elif (found.lower() == 'n'):
                    referencePhoto = np.copy(globals.currentPhoto)
                    cv2.imwrite('referencePhoto.jpg', referencePhoto)
        resets += 1