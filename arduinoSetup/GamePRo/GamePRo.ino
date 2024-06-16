//Speacial thanks to Westini who helped tidy the original GamePRo standard sketch to its current form.
#include <Servo.h> 

#define NEWLINE '\n'
#define READ_LIGHT 'B'
#define READ_LIGHT_ADVANCED 'C'
#define LIGHT_LOW 'L'
#define LIGHT_HIGH 'H'
#define HOLD_UP '8'
#define HOLD_DOWN '2'
#define HOLD_LEFT '4'
#define HOLD_RIGHT '6'
#define PRESS_UP 'e'
#define PRESS_DOWN 'd'
#define PRESS_LEFT 's'
#define PRESS_RIGHT 'f'
#define BUTTON_A 'a'
#define BUTTON_B 'b'
#define BUTTON_X 'x'
#define BUTTON_Y 'y'
#define RELEASE_ALL '0'
#define SOFT_RESET_1 'S'
#define SOFT_RESET_2 'Z'
#define WONDER_TRADE 'W' 

Servo myservo_1;
Servo myservo_2;
Servo myservo_3;
Servo myservo_4;
Servo myservo_5;

// Set variables for left and right buttons
int leftMax = 80;
int rightMax = 100;
int leftrightOff = 90; 

// Set variables for up and down buttons
int upMax = 80;
int downMax = 100;
int updownOff = 90;

// Set variables for A and Y buttons
int YMax = 80;
int AMax = 100;
int AYOff = 90;

// Set variables for B and X buttons
int BMax = 80;
int XMax = 100;
int BXOff = 90;

// Set variables for Soft Reset
int SRMax = 80; 
int SROff = 90;
int WMax = 100;

int arrowBackoffU = 5;
int arrowBackoffD = 5;
int arrowBackoffL = 5;
int arrowBackoffR = 5;


int arrow_releaseU=100;
int arrow_releaseD=100;
int arrow_releaseL=100;
int arrow_releaseR=100;
int button_release=120;
int prePress=200;
int lightCutoff = 150;
int LDR = 0;//pin assignment for LDR
int v1 = 0;
char b1;

void setup()
{
  Serial.begin(9600);
  myservo_1.attach(7);
  myservo_2.attach(8);
  myservo_3.attach(3);
  myservo_4.attach(2);
  myservo_5.attach(6);
  pinMode(LDR, INPUT);

  myservo_1.write(leftrightOff); 
  myservo_2.write(updownOff); 
  myservo_3.write(AYOff);
  myservo_4.write(BXOff);
  myservo_5.write(SROff);
}

void loop()
{
  if (Serial.available() > 0)
  {   
    int letter = Serial.read();
    if((letter != NEWLINE)&&(letter !=READ_LIGHT)&&(letter != READ_LIGHT_ADVANCED))
    {
      releaseAll();
    }     

    switch (letter) {

      //Compare Light sensor reading to cutoff value and return if it is higher of lower
      case READ_LIGHT:
        v1 = analogRead(LDR);        
      
        if(v1 < lightCutoff)
        {
          Serial.print(LIGHT_LOW);  
        }
        else
        {
          Serial.print(LIGHT_HIGH);
        }
        break;

       //Take reading from light sensor, reduce range by factor of 4 and send to serial
      case READ_LIGHT_ADVANCED:
        v1 = analogRead(LDR); 
        delay(10); 

        b1=v1/4;
        
        Serial.print(b1);
        break;

        
      case HOLD_UP:
        myservo_2.write(upMax);
        delay(prePress);
        myservo_2.write(upMax+arrowBackoffU);
        break;
      case PRESS_UP:
        myservo_2.write(upMax);
        delay(arrow_releaseU);
        myservo_2.write(updownOff);
        break;
      case HOLD_LEFT:
        myservo_1.write(leftMax);
        delay(prePress);
        myservo_1.write(leftMax+arrowBackoffL);  
        break;
      case PRESS_LEFT:
        myservo_1.write(leftMax);
        delay(arrow_releaseL);
        myservo_1.write(leftrightOff);
        break;
      case HOLD_DOWN:
        myservo_2.write(downMax);
        delay(prePress);
        myservo_2.write(downMax-arrowBackoffD);
        break;
      case PRESS_DOWN:
        myservo_2.write(downMax);
        delay(arrow_releaseD);
        myservo_2.write(updownOff);
        break;
      case HOLD_RIGHT:
        myservo_1.write(rightMax);
        delay(prePress); 
        myservo_1.write(rightMax-arrowBackoffR); 
        break;
      case PRESS_RIGHT:
        myservo_1.write(rightMax);
        delay(arrow_releaseR);
        myservo_1.write(leftrightOff);
        break;
      case BUTTON_Y:
        myservo_3.write(YMax);
        delay(button_release);
        myservo_3.write(AYOff);  
        break;
      case BUTTON_B:
        myservo_4.write(BMax);
        delay(button_release);
        myservo_4.write(BXOff); 
        break;
      case BUTTON_X:
        myservo_4.write(XMax);
        delay(button_release);
        myservo_4.write(BXOff); 
        break;
      case BUTTON_A:
        myservo_3.write(AMax);
        delay(button_release);
        myservo_3.write(AYOff);
        break;   

      case SOFT_RESET_1:
        myservo_5.write(SRMax);
        delay(250);
        myservo_5.write(SROff); 
        break;

      case SOFT_RESET_2:
        myservo_5.write(SRMax);
        myservo_3.write(AMax);
        myservo_4.write(BMax);     
        delay(250);
        myservo_5.write(SROff); 
        myservo_3.write(AYOff);
        myservo_4.write(BXOff); 
        break;
        
      case WONDER_TRADE:
        myservo_5.write(WMax);
        delay(250);
        myservo_5.write(SROff); 
        break;
      case RELEASE_ALL:
        releaseAll();
        break;
    }
  }
}

void releaseAll() {
  myservo_1.write(leftrightOff); 
  myservo_2.write(updownOff); 
  myservo_3.write(AYOff);
  myservo_4.write(BXOff);
  myservo_5.write(SROff);
}
