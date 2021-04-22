int analogPin = 1;
int command = 0;
int value = 0;
int meas = 0;

byte b1, b2;

int avg_num = 10;

void setup() {
  Serial.begin(9600);
}

void loop() {
  value = Serial.read();
  
  delay(100);
  
  if(value == 'n') {
    meas = 1023 - analogRead(analogPin);

    b1 = meas&0xFF;
    b2 = ( meas >> 8 ) & 0xFF;

    Serial.write(b1);
    delay(100);
    Serial.write(b2);

    //Serial.println(meas);
    //Serial.println(b1);
    //Serial.println('\n');
    //Serial.println(b2);
    delay(100);
  }

  // from https://forum.arduino.cc/t/calculating-average-of-analog-read-values/427104
  else if(value == 'a') {
      for (int n=0; n<avg_num; n++) {
        meas = ((1023 - meas) * n-1 + analogRead(analogPin)) / n ;
      }

      b1 = meas&0xFF;
      b2 = ( meas >> 8 ) & 0xFF;
  
      Serial.write(b1);
      delay(100);
      Serial.write(b2);
      delay(100);
  }

  // placeholder for other detector types
  else if(value == 'c') {
    delay(100)  
  }
}
