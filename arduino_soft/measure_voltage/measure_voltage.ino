int analogPin = 1;
int command = 0;
int value = 0;
int meas;

byte b1, b2;

void setup() {
  Serial.begin(9600);
}

void loop() {
  value = Serial.read();
  
  delay(100);
  
  if(value == 't') {
    meas = analogRead(analogPin);

    b1 = meas&0xFF;
    b2 = ( meas >> 8 ) & 0xFF;

    Serial.write(b1);
    delay(100);
    Serial.write(b2);

    Serial.println(meas);
    //Serial.println(b1);
    //Serial.println('\n');
    //Serial.println(b2);
    delay(100);
  }
}
