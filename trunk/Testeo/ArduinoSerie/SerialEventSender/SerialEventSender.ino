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
long int a=0, b=0, c=0, d=0, e=0, f=0, g=0, h=0, i=0, j=0, k=0, l=0, m=0, n=0, o=0, p=0;
  
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
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, a));
          break;
        case 1:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, b));
          break;
        case 2:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, c));
          break;
        case 3:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, d));
          break;
        case 4:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, e));
          break;    
        case 5:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, f));
          break;
        case 6:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, g));
          break;
        case 7:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, h));
          break;          
        case 8:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, i));
          break;
        case 9:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111,j));
          break;
        case 10:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, k));
          break;
        case 11:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, l));
          break;
        case 12:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, m));
          break;    
        case 13:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, n));
          break;
        case 14:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, o));
          break;
        case 15:
          sprintf(concat,"%c#%ld",Celdas[i],random(1111, p));
          break;
        default:
          break;

      }
      sprintf(concat,"%s#%d",concat,random(1111, 9999));
      Serial.println(concat); 
      //delay(1);
      //1,2 mili segundos como en el Hard
      //0,0012 = 1,2MILI = 1200 da 0,00175 de promedio entre cada celda
      //0,0009 = 0,9MILI = 900 da  0,00155 de promedio entre cada celda
      //0,0006 = 0,6MILI = 600 da  0,00105 de promedio entre cada celda
      delayMicroseconds(70);
    }
      
     if (Serial.available() != 0) {
         delay(1);
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

        case 'f':
          f=4444;
          Serial.println("OK");
          break;
          
        case 'g':
          g=3333;
          Serial.println("OK");
          break;
          
        case 'h':
          h=2222;
          Serial.println("OK");
          break;
          
        case 'i':
          i=1111;
          Serial.println("OK");
          break;

        case 'j':
          j=8989;
          Serial.println("OK");
          break;
          
        case 'k':
          k=9898;
          Serial.println("OK");
          break;
          
        case 'l':
          l=1717;
          Serial.println("OK");
          break;
          
        case 'm':
          m=5656;
          Serial.println("OK");
          break;
          
        case 'n':
          n=3232;
          Serial.println("OK");
          break;
          
        case 'o':
          o=9090;
          Serial.println("OK");
          break;
          
        case 'p':
          p=9909;
          Serial.println("OK");
          break; 
          
        default:
          Serial.println("NOK");
      }        
               
     }
  }
}



