boolean a=true;
boolean b=true;
boolean c=false;
boolean d=false;
boolean e=true;
boolean f=true;
boolean g=false;
boolean h=false;

boolean led=false;

char inByte=0;

void setup() {                
  // initialize the digital pin as an output.
  // Pin 13 has an LED connected on most Arduino boards:
  pinMode(13, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);

//  digitalWrite(13,HIGH);
//  delay(250);
//  digitalWrite(13,LOW);
//  delay(250);
//  digitalWrite(13,HIGH);
//  delay(250);
//  digitalWrite(13,LOW);

  Serial.begin(9600);

  digitalWrite(10,a);
  digitalWrite(2,b);
  digitalWrite(3,c);
  digitalWrite(4,d);
  digitalWrite(5,e);
  digitalWrite(6,f);
  digitalWrite(7,g);
  digitalWrite(8,h);  

  display_values();
  
}

void display_values() {
  
  Serial.print('x');

  if (h == true) 
    Serial.print("1");
  else
    Serial.print("0");

  if (a == true) 
    Serial.print("1");
  else
    Serial.print("0");

  if (b == true) 
    Serial.print("1");
  else
    Serial.print("0");

  if (c == true) 
    Serial.print("1");
  else
    Serial.print("0");

  if (d == true) 
    Serial.print("1");
  else
    Serial.print("0");

  if (e == true) 
    Serial.print("1");
  else
    Serial.print("0");

  if (f == true) 
    Serial.print("1");
  else
    Serial.print("0");

  if (g == true) 
    Serial.print("1");
  else
    Serial.print("0");
  
  Serial.println();
}

void loop() {
  //if (led == true) {
  //  led = false;
  //} else {
  //  led = true;
  //}
  //digitalWrite(13,led);
  digitalWrite(10,a);
  digitalWrite(2,b);
  digitalWrite(3,c);
  digitalWrite(4,d);
  digitalWrite(5,e);
  digitalWrite(6,f);
  digitalWrite(7,g);
  digitalWrite(8,h);  
  while (Serial.available() == 0); // pause until a byte is received by serial Rx
  inByte = Serial.read();
  if (inByte == 'x') {
      while (Serial.available() == 0);
      inByte = Serial.read();
      h = (inByte =='1');
      while (Serial.available() == 0);
      inByte = Serial.read();
      g = (inByte =='1');
      while (Serial.available() == 0);
      inByte = Serial.read();
      f = (inByte =='1');
      while (Serial.available() == 0);
      inByte = Serial.read();
      e = (inByte =='1');
      while (Serial.available() == 0);
      inByte = Serial.read();
      d = (inByte =='1');
      while (Serial.available() == 0);
      inByte = Serial.read();
      c = (inByte =='1');
      while (Serial.available() == 0);
      inByte = Serial.read();
      b = (inByte =='1');
      while (Serial.available() == 0);
      inByte = Serial.read();
      a = (inByte =='1');
  }

  display_values();  
  //Serial.println(char(a),char(b),char(c),char(d),char(e),char(f),char(g),char(h));
  //Serial.println(a, b, c, d, e, f, g ,h);

}

