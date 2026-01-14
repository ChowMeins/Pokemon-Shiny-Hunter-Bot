import time
import serial
from serial.tools import list_ports
import threading
from ultralytics import YOLO
import cv2
from webcam import WebcamStream
import threading

if __name__ == "__main__":
    # List and select serial port to connect to
    list_ports_list = list_ports.comports()
    print("Select a port to connect to:\n")
    for i, port in enumerate(list_ports_list):
        print(f'{i} : {port}')
    userInput = int(input("\nWhich port would you like to connect to?\n"))
    print(list_ports_list[userInput].name)
    ser = serial.Serial(port=list_ports_list[userInput].name, baudrate=9600, timeout=10)

    # Start webcam thread
    webcam = WebcamStream(show_feed=True)
    webcam.start()

    # Load Model
    model = YOLO("best.pt", task="obb")  # Load a pretrained YOLOv8n model

    # Input direction and length of path to hunt
    direction_input = int(input("Enter direction to hunt: (0 = up/down, 1 = left/right): "))
    while direction_input not in [0, 1]:
        direction_input = int(input("Invalid input. Enter direction to hunt: (0 = up/down, 1 = left/right): "))
    direction = ['u', 'd'] if direction_input == 0 else ['l', 'r']
    path_length = int(input("Enter length of path to hunt (number of tiles): "))
    delay_time = 125 * path_length # in milliseconds
    
    # Loop to send commands to arduino
    stop = False
    while not stop:
        if ser.in_waiting > 0:
            input_line = ser.readline().decode('utf-8', errors='ignore').strip()
            for d in direction:
                if input_line == 'READY':
                    ser.write(f'{d} {delay_time}\n'.encode('utf-8'))  # Move up/down
            input_line = None
            result = model.predict(source=webcam.get_frame())
            print(result)
            boxes = result[0].boxes
            if boxes != None and len(boxes) > 0:
                print(f"Detected {len(boxes)} objects!")
                for box in boxes:
                    print(box.xyxy)  # bounding box coordinates
                    print(box.cls)   # class ID
                    print(model.names[int(box.cls)])  # class name
            else:
                print("No detections in this image")

    