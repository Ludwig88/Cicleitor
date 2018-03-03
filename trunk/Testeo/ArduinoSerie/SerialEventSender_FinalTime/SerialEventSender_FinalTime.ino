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
int led = 13;
int state = 0;

void setup() {
  // initialize serial:
  Serial.begin(115200);
  // reserve 200 bytes for the inputString:
  pinMode(led, OUTPUT);
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
      delayMicroseconds(60);
      //delay(1);
    }
      
     if (Serial.available() != 0) {
       
       delay(1);
       //delayMicroseconds(60);
       recibo=Serial.read();
       state = !state;
        
      switch (recibo) {
        case 'a':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            a=9999;
          }
          else {
            a=1111;
          }
          Serial.println("ok");
          break;
          
        case 'b':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            b=8888;
          }
          else {
            b=1111;
          }
          Serial.println("ok");
          break;
          
        case 'c':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            c=8888;
          }
          else {
            c=1111;
          }
          Serial.println("ok");
          break;
          
        case 'd':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            d=8888;
          }
          else {
            d=1111;
          }
          Serial.println("ok");
          break;
          
        case 'e':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            e=8888;
          }
          else {
            e=1111;
          }
          Serial.println("ok");
          break;

        case 'f':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            f=8888;
          }
          else {
            f=1111;
          }
          Serial.println("ok");
          break;
          
        case 'g':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            g=8888;
          }
          else {
            g=1111;
          }
          Serial.println("ok");
          break;
          
        case 'h':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            h=8888;
          }
          else {
            h=1111;
          }
          Serial.println("ok");
          break;
          
        case 'i':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            i=8888;
          }
          else {
            i=1111;
          }
          Serial.println("ok");
          break;

        case 'j':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            j=8888;
          }
          else {
            j=1111;
          }
          Serial.println("ok");
          break;
          
        case 'k':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            k=8888;
          }
          else {
            k=1111;
          }
          Serial.println("ok");
          break;
          
        case 'l':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            l=8888;
          }
          else {
            l=1111;
          }
          Serial.println("ok");
          break;
          
        case 'm':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            m=8888;
          }
          else {
            m=1111;
          }
          Serial.println("ok");
          break;
          
        case 'n':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            n=8888;
          }
          else {
            n=1111;
          }
          Serial.println("ok");
          break;
          
        case 'o':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            o=8888;
          }
          else {
            o=1111;
          }
          Serial.println("ok");
          break;
          
        case 'p':
          digitalWrite(led, (state) ? HIGH : LOW);
          if(state){
            p=8888;
          }
          else {
            p=1111;
          }
          Serial.println("ok");
          break;
          
        default:
          Serial.println("nok");
      }        
               
     }
  }
}



