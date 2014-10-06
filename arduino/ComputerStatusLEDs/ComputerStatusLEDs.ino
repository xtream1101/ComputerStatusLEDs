
char* MODEL = "XN-LED4-5C9F";
int numLeds = 4;
//How many of the shift registers - change this
#define numShifts 2

///////////////////
//  DO NOT EDIT  //
///////////////////
int latchPin = 5;
int clockPin = 6;
int dataPin = 4;

#define numShiftsPins numShifts * 8

boolean registers[numShiftsPins];
String cmd;
char colorList[] = {'R', 'G', 'B'};
int ledState[numShiftsPins];

void setup(){
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);  
  pinMode(clockPin, OUTPUT);
  Serial.begin(9600);
  //Set all leds to off/0
  for(int i=0;i<=sizeof(ledState);i++){
    ledState[i] = 0; 
  }
  updateShiftRegister();
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
            if(cmd[1] == colorList[j] || cmd[1] == 'A' ){
              if(cmd[2] == '1')      ledState[stateIJ] = 1;
              else if(cmd[2] == 'T') ledState[stateIJ] = !ledState[stateIJ];
              else                   ledState[stateIJ] = 0;
            }
          } //END for(j)
        }
      } //END for(i)
      updateShiftRegister();
    } //END if(?)
    cmd="";
  } //END if(cmd.length) 
} //END loop()

void updateShiftRegister(){
  digitalWrite(latchPin, LOW);
  for(int i = numShiftsPins - 1; i >=  0; i--){
    digitalWrite(clockPin, LOW);
    digitalWrite(dataPin, ledState[i]);
    digitalWrite(clockPin, HIGH);
  }
  digitalWrite(latchPin, HIGH);
  
} //END updateShiftRegister()
