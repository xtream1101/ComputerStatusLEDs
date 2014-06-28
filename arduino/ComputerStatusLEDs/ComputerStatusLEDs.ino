int latchPin = 5;
int clockPin = 6;
int dataPin = 4;

String cmd;

byte leds = B00000000;
byte rgb[] = {B10000000, B01000000, B00100000, B00010000, 
              B00001000, B00000100, B00000010, B00000001}; 
boolean ledState[] = {false, false, false, false, 
                      false, false, false, false};
/*
  0 - 1R
  1 - 1G
  2 - 1B 
  3 - 2R
  4 - 2G
  5 - 2B
  6 - N/A
  7 - N/A
*/


void setup(){
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);  
  pinMode(clockPin, OUTPUT);
  Serial.begin(9600);
  setLeds();
} //END setup()
 
void loop(){
  while(Serial.available()){
    delay(3);  //delay to allow buffer to fill 
    if (Serial.available() > 0){
      char c = Serial.read();
      cmd += c; 
    } 
  }

  if(cmd.length() > 0){
    if(cmd[0] == '1'){
      if(cmd[1] == 'R')
        if(cmd[2] == '1')      ledState[0] = true;
        else if(cmd[2] == 'T') ledState[0] = !ledState[0];
        else                   ledState[0] = false;
      if(cmd[1] == 'G')
        if(cmd[2] == '1')      ledState[1] = true;
        else if(cmd[2] == 'T') ledState[1] = !ledState[1];
        else                   ledState[1] = false;
      if(cmd[1] == 'B')
        if(cmd[2] == '1')      ledState[2] = true;
        else if(cmd[2] == 'T') ledState[2] = !ledState[2];
        else                   ledState[2] = false;
      
    }else if(cmd[0] == '2'){
      if(cmd[1] == 'R')
        if(cmd[2] == '1')      ledState[3] = true;
        else if(cmd[2] == 'T') ledState[3] = !ledState[3];
        else                   ledState[3] = false;
      if(cmd[1] == 'G')
        if(cmd[2] == '1')      ledState[4] = true;
        else if(cmd[2] == 'T') ledState[4] = !ledState[4];
        else                   ledState[4] = false;
      if(cmd[1] == 'B')
        if(cmd[2] == '1')      ledState[5] = true;
        else if(cmd[2] == 'T') ledState[5] = !ledState[5];
        else                   ledState[5] = false;
    } 
    cmd="";
    setLeds();
  } 
} //END loop()

void setLeds(){
  leds = B00000000;
  for(int i=0; i < sizeof(rgb); i++){
    if(ledState[i]) 
      leds = leds | rgb[i];
  } 
  updateShiftRegister();  
} //END setLeds()

void updateShiftRegister(){
   digitalWrite(latchPin, LOW);
   shiftOut(dataPin, clockPin, LSBFIRST, leds);
   digitalWrite(latchPin, HIGH);
} //END updateShiftRegister()
