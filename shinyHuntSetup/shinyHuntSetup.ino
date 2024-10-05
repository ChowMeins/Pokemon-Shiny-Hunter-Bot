#include <Servo.h>
using namespace std;

Servo servo1; // Pin 2, controls buttons B and X
Servo servo2; // Pin 3, controls buttons A and Y
Servo servo3; // 
Servo servo4;
Servo servo5;
Servo servos[5];
int servoPins[] = {2,3,6,7,8};
int sensorPin = A0;
int sensor;

int input;
int defaultPos = 90;
int aPos = 150;
int bPos = 55;
int xPos = 145;
int yPos = 50;
int uPos = 30;
int dPos = 120;
int rPos = 140;
int lPos = 60;
int resetPos = 15;
/* 
Servo 1 = B and X
Servo 2 = A and Y
Servo 3 = Start + Select
Servo 4 = L and R
Servo 5 = U and D
*/
void sendInput(Servo servo, int rotationAmount, int delayTime) {
  int currRotation = servo.read();
  // Initiate actuation of arduino
  while(currRotation != rotationAmount) {
    currRotation = servo.read();
    if(currRotation < rotationAmount) {
      currRotation++;
    } else {
      currRotation--;
    }
    servo.write(currRotation);
    delay(2.5);
  }
  delay(delayTime);

  // Release servo from button
  while(currRotation != defaultPos) {
      currRotation = servo.read();
    if(currRotation < defaultPos) {
      currRotation++;
    }
    else {
      currRotation--;
    }
    servo.write(currRotation);
    delay(2.5);
  }
}
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for(int i = 0; i < sizeof(servos); ++i) {
    servos[i].attach(servoPins[i]);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
    String inputString = Serial.readStringUntil('\n');
    if (inputString == "light") {
      Serial.println(analogRead(sensorPin));
    }
    else {
      input = inputString[0];
      int delayTime = inputString.substring(1, inputString.length()).toInt();
      delayTime = delayTime < 100 ? 100 : delayTime;

      if (input != '\0') {
        //Serial.print(input); Serial.print(", "); Serial.print(delayTime); Serial.print("\n\0");
        switch(input) {
            case 'a':
              sendInput(servos[1], aPos, delayTime);
              break;
            case 'b':
              sendInput(servos[0], bPos, delayTime);
              break;
            case 'x':
              sendInput(servos[0], xPos, delayTime);
              break;
            case 'y':
              sendInput(servos[1], yPos, delayTime);
              break;
            case 'u':
              sendInput(servos[4], uPos, delayTime);
              break;
            case 'd':
              sendInput(servos[4], dPos, delayTime);
              break;
            case 'l':
              sendInput(servos[3], lPos, delayTime);
              break;
            case 'r':
              sendInput(servos[3], rPos, delayTime);
              break;
            case 'e':
              sendInput(servos[2], resetPos, delayTime);
              break;
            case 'f':
              Serial.flush();
              break;
          break;
        }
      }
    }
}
