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
    for (int i=0;i<16;i++) {
      switch (i) {
        case 0:
          sprintf(concat,"%c#%d",Celdas[i],random(1111, a));
          break;
        case 1:
          sprintf(concat,"%c#%d",Celdas[i],random(1111, b));
          break;
        case 2:
          sprintf(concat,"%c#%d",Celdas[i],random(1111, c));
          break;
        case 3:
          sprintf(concat,"%c#%d",Celdas[i],random(1111, d));
          break;
        case 4:
          sprintf(concat,"%c#%d",Celdas[i],random(1111, e));
          break;          
        default:
          sprintf(concat,"%c#%d",Celdas[i],random(1111, 10));
          break;

      }
      sprintf(concat,"%s#%d",concat,random(1111, 9999));
      Serial.println(concat); 
      delay(1);
    }
      
     if (Serial.available() != 0) {
        recibo=Serial.read();
        
      switch (recibo) {
        case 'a':
          a=9999;
          Serial.println("OK");
          break;
          
        case 'b':
          b=8888;
          Serial.println("OK");
          break;
          
        case 'c':
          c=7777;
          Serial.println("OK");
          break;
          
        case 'd':
          d=6666;
          Serial.println("OK");
          break;
          
        case 'e':
          e=5555;
          Serial.println("OK");
          break;
          
        default:
          Serial.println("NOK");
      }        
               
     }
  }
}



