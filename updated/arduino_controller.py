import time
import serial
from serial.tools import list_ports
import threading
from ultralytics import YOLO
import cv2
from webcam import WebcamStream
import threading

class ArduinoController():
    def __init__(self, port, baudrate=9600, timeout=10):
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.running = False
        self.hunt_type = None
        self.tile_count = 0
        self.thread = None

    def start(self):
        """Start the Arduino communication thread"""
        self.running = True
        if self.hunt_type == "hgss_random_encounters":
            self.thread = threading.Thread(target=self.hgss_random_encounters, daemon=True)
        self.thread.start()
    
    def hgss_random_encounters(self):
        while self.running == True:
            self.ser.write("d")
    