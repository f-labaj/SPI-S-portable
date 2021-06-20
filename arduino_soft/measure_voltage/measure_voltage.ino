int analogPin = 1;
int command = 0;
int value = 0;
int meas = 0;
int temp_meas = 0;

byte b1, b2;

int avg_num = 20;
int sample_num = 2000;

void setup() {
  Serial.begin(9600);
}

void loop() {
  value = Serial.read();
  
  delay(100);
  
  if(value == 'n') {
    delay(150);
    
    meas = analogRead(analogPin);

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
      delay(150);
      
      for (int n=0; n<avg_num; n++) {
        meas = ((meas) * n-1 + analogRead(analogPin)) / n ;
      }

      b1 = meas&0xFF;
      b2 = ( meas >> 8 ) & 0xFF;
  
      Serial.write(b1);
      delay(100);
      Serial.write(b2);
      delay(100);

      meas = 0;
  }

  else if(value == 'x') {
      int temp = 0;
      for (int n=0; n<sample_num; n++) {
          temp = analogRead(analogPin);
          if(temp > meas){
            meas = temp;
          }
      }

      //meas = 1024 - meas;

      b1 = meas&0xFF;
      b2 = ( meas >> 8 ) & 0xFF;
  
      Serial.write(b1);
      delay(100);
      Serial.write(b2);
      delay(100);

      meas = 0;
    }

  // placeholder for other detector types
  else if(value == 'c') {
    delay(100);  
  }
}
