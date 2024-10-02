# This program is a simple program to test that the arduino is properly connected to the program.
import serial
import time
import cv2
import threading
import globals
from BW2Starter import BW2Starter
from HGSSRandomEncounters import HGSSRandomEncounters
from webcam import record, requestFeed

def readSensor():
    while(True):
        globals.sensorVal = globals.ser.readline().decode('ASCII').strip().split(", ")
        print(globals.sensorVal)

if __name__ == '__main__':
    # Connect to Arduino
    print("Connecting to Arduino...")
    globals.ser = serial.Serial(port='COM6', baudrate=9600, timeout=5)
    print("Connected to", globals.ser.name)
    time.sleep(2)

    option = input("Enter an option (press a number):\n1.) Pokemon BW2 Starter\n2.) Pokemon HGSS Safari Zone Encounters\n")
    print("Loading webcam...")
    # Connect to Webcam
    globals.vid = cv2.VideoCapture(0)
    if (globals.vid):
        print("Webcam loaded. Opening window...")
    else:
        exit()
    t1 = threading.Thread(target=record)
    t1.daemon = True
    t1.start()

    # Remove every photo in directory
    #path = './encounters'
    #dir = os.listdir(path)
    #for file in dir:
    #    os.remove(path + '/' + file)

    print(option)
    if (option == "1"):
        t2 = threading.Thread(target=BW2Starter)
        t2.start()
    elif (option == "2"):
        t2 = threading.Thread(target=HGSSRandomEncounters)
        t2.start()

    t3 = threading.Thread(target=readSensor)
    t3.start()

    t1.join()
    t2.join()
    t3.join()


    print("Program terminating...")
    # Close all windows
    globals.vid.release()
    cv2.destroyAllWindows()
