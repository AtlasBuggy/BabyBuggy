/* 
  IR Breakbeam sensor demo!
*/
#include <Atlasbuggy.h>
 
#define SENSORPIN 4
 
int sensorState = 0, lastState=0, ticks = 0;
 
Atlasbuggy robot("encoder");

void setup() {
  robot.begin();
}
void loop(){
  // read the state of the pushbutton value:
  sensorState = digitalRead(SENSORPIN);
  
  if (sensorState && !lastState) {
    //Serial.println("Unbroken");
    ticks++;
    Serial.print("e%d\n",ticks);
  } else if (!sensorState && lastState) {
    //Serial.println("Broken");
    ticks++;
    Serial.print("e%d\n",ticks);
  }
  lastState = sensorState;
}

