int latchPin = 5;
int clockPin = 6;
int dataPin = 4;

char* MODEL = "XN-LED2-5C95";

String cmd;
char colorList[] = {'R', 'G', 'B'};
int numLeds = 2;
byte leds = 0;
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
    if(cmd[0] == '?'){
      Serial.write(MODEL);
    }else{
      for(int i=1; i<=numLeds; i++){
        int stateI = i*3;
        if(cmd[0]-'0' == i){
          for(int j=0; j<sizeof(colorList); j++){
            int stateJ = j-3;
            int stateIJ = stateI + stateJ;
            if(cmd[1] == colorList[j]){
              if(cmd[2] == '1')      ledState[stateIJ] = true;
              else if(cmd[2] == 'T') ledState[stateIJ] = !ledState[stateIJ];
              else                   ledState[stateIJ] = false;
            }
          } //END for(j)
        }
      } //END for(i)
      setLeds();
    } //END if(?)
    cmd="";
  } //END if(cmd.length) 
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
