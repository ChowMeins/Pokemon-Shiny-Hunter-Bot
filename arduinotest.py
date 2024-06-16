import serial
import time

ser = serial.Serial(port='COM3', baudrate=9600, timeout=5)
print("Connected to", ser.name)
time.sleep(2)

while(True):    
    send_command = input("Enter a button to press('A', 'B', 'X', 'Y'):")
    send_command = (bytes(send_command.lower(), 'UTF-8'))
    ser.write(send_command)
    if (send_command == 'exit'):
        break
    #print(str(ser.readline()))