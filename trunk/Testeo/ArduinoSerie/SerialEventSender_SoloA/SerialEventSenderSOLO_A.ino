/*
  Serial Event example
 
 When new serial data arrives, this sketch adds it to a String.
 When a newline is received, the loop prints the string and 
 clears it.
 
 A good test for this is to try it with a GPS receiver 
 that sends out NMEA 0183 sentences. 
 
 Created 9 May 2011
 by Tom Igoe
 
 This example code is in the public domain.
 
 http://www.arduino.cc/en/Tutorial/SerialEvent
 
 */
char concat[80];
int recibo=0;
char Celdas[]={'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p'};
int a=0, b=0, c=0, d=0, e=0;
  
void setup() {
  // initialize serial:
  Serial.begin(115200);
  // reserve 200 bytes for the inputString:
  //inputString.reserve(200);
}

void loop() {
  while (true) {
      sprintf(concat,"a#%d",random(1000, 9999));
      sprintf(concat,"%s#%d\n",concat,random(100, 999));
      Serial.print(concat); 
      delay(1);
    }
}



