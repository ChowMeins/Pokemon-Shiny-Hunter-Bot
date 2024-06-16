#define LED_BUILTIN 13

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  String input = Serial.readString();
  if (input == "on") {
    digitalWrite(LED_BUILTIN, HIGH);
  }
  else if (input == "off") {
    digitalWrite(LED_BUILTIN, LOW);
  }
}
