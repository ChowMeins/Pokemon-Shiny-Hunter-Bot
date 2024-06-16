#include <Servo.h>

Servo servo1; // Pin 2, controls buttons B and X
Servo servo2; // Pin 3, controls buttons A and Y
Servo servo3; // 
Servo servo4;
Servo servo5;
Servo servos[5];
int servoPins[] = {2,3,6,7,8};
char input;
int defaultPos = 90;
int aPos = 170;
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
void sendInput(Servo servo, int rotationAmount) {
  //servo.write(rotationAmount);
  
  while(servo.read() != rotationAmount) {
    int currRotation = servo.read();
    if(servo.read() < rotationAmount) {
      servo.write(currRotation + 1);
      delay(2.5);
    }
    else if (servo.read() > rotationAmount)  {
      servo.write(currRotation - 1);
      delay(2.5);
    }
  }
  delay(100);
  while(servo.read() != defaultPos) {
    int currRotation = servo.read();
    if(servo.read() < defaultPos) {
      servo.write(currRotation + 1);
      delay(2.5);
    }
    else if (servo.read() > defaultPos)  {
      servo.write(currRotation - 1);
      delay(2.5);
    }
  }
  
  //servo.write(defaultPos);
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
    input = Serial.read();
    if (input != NULL) {
    //Serial.print(input);
    switch(input) {
        case 'a':
          sendInput(servos[1], aPos);
          break;
        case 'b':
          sendInput(servos[0], bPos);
          break;
        case 'x':
          sendInput(servos[0], xPos);
          break;
        case 'y':
          sendInput(servos[1], yPos);
          break;
        case 'u':
          sendInput(servos[4], uPos);
          break;
        case 'd':
          sendInput(servos[4], dPos);
          break;
        case 'l':
          sendInput(servos[3], lPos);
          break;
        case 'r':
          sendInput(servos[3], rPos);
          break;
        case 'e':
          sendInput(servos[2], resetPos);
          break;
        case 'f':
          Serial.flush();
          break;
      break;
      }
    }
}
