from globals import stop_threads, requestFeed, referencePhoto, currentPhoto, webcam, pixel, resets, sensorVal, ser, vid
import time

def sendCommand(ser, command, delay):
    globals.ser.write(bytes(command, 'UTF-8'))
    time.sleep(delay)

def HGSSRandomEncounters():
    global stop_threads
    global referencePhoto
    global currentPhoto
    global requestFeed
    global pixel
    global resets
    global webcam

    tileCount = input("Enter the number of tiles of grass from left to right.\n")
    delay = str(150 * int(tileCount))
    while not stop_threads:
        encounterFound = False
        while (encounterFound == False):
            sendCommand(ser, 'l' + delay , 2)
            sendCommand(ser, 'r' + delay , 2)
