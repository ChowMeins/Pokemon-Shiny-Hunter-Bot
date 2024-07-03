# Pokemon Shiny Hunting Bot

This is a shiny hunting program created for Pokemon Black and White 2 to shiny hunt the starter Pokemon.
Currently, this version supports hunting the starter Tepig.

The program utilizes the Game PRo for the 3DS.
You can find the hardware here: https://www.noobysgamepro.com/

Connect the Arduino and Webcam to your PC.
In order to use this program, you must upload the shinyHuntSetup.ino to the Arduino Nano and make sure you are connected to the right COM port.
Once uploaded, run the Python program.

## **First image** <br/>
![image](https://github.com/ChowMeins/Pokemon-Shiny-Hunter-Bot/assets/101289297/ca9f0802-5bfa-432a-8120-a103feb225e7)

## **Final Results** <br/>
![image](https://github.com/ChowMeins/Pokemon-Shiny-Hunter-Bot/assets/101289297/99df5469-38aa-4cb5-9e82-29608a425a1b)

Flaws:
Some flaws with the program is that the webcam doesn't have the greatest quality at all times, meaning that initializing the first reference photo
may be blurry, but should still yield a shiny.

The servos that actuate the buttons the 3DS are slow moving, which is not ideal, but is needed (in my experience) to prolong the longetivity of the servo motors.
