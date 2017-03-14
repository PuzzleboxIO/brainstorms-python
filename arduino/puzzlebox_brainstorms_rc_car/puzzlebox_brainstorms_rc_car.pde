/*                                                                                                                                          /*
 
 Puzzlebox - Brainstorms - RC Car - Arduino Control
 
 Copyright Puzzlebox Productions, LLC (2011)
 
 This code is released under the GNU Pulic License (GPL) version 2
 For more information please refer to http://www.gnu.org/copyleft/gpl.html 
 
 Modified 2011-06-20
 By Steve Castellotti

 References: 
 http://arduino.cc/en/Tutorial/AnalogInput
 http://arduino.cc/en/Reference/Map
 http://www.arduino.cc/playground/Main/TimerPWMCheatsheet
 http://principialabs.com/arduino-pulse-width-modulation/
 
 */

int DEBUG = 2;

int ledPin = 13;         // select the pin for the LED

char serialDelimiter = '!'; // character to specify the boundary between separate, 
                            // independent regions in data stream
char axisDelimiter = ',';   // character to specify the boundary between throttle and steering

int delayValue = 5000;   // loop delay in milliseconds
//int delayMultiplier = (float)62500 / (float)976.5625;
//int delayMultiplier = (float)31250 / (float)488.28125;
int delayMultiplier = 1;

int sensorPin = A0;      // select the input pin for the potentiometer
int sensorValue = 0;     // variable to store the value coming from the sensor
int testSensorPin = A1;  // input pin for simulation testing output PWM
int testSensorValue = 0; // variable to test the value coming from the output pin

int outputValueThrottle = 0; // variable to store the throttle output PWM value
int outputPinThrottle = 9;   // PWM output pin
float outputVoltageThrottle = 0.0;

int outputValueSteering = 0; // variable to store the steering output PWM value
int outputPinSteering = 10;  // PWM output pin
float outputVoltageSteering = 0.0;

//int neutralValueThrottle = 351; // neutral 1.64v (Arduino 353-356)
int neutralValueThrottle = 342; // neutral 1.64v (Arduino 353-356)
int forwardValue = 415;         // forward 1.91v (Arduino 415-418)
int reverseValue = 312;         // reverse 1.47v (Arduino 311-314)
int neutralValueSteering = 342; // neutral 1.64v
int leftValue = 420;            // left    1.20v
int rightValue = 310;           // right   2.05v

char inputByte = '0';
char inputSign = '+';
char inputValueString[4] = "000";
int inputValue = 0;

float ratio;

void setup() {
  
  // NOTE: Timer defaults are 0x04 - 976.5625, 488.28125, 488.28125 respectively
  // Set Pins 5 & 6 (Timer0) frequency to 976.5625Hz or 62.5Khz
  TCCR0B = TCCR0B & 0b11111000 | 0x04; // 976.5625Hz
  //TCCR0B = TCCR0B & 0b11111000 | 0x01; // 62.5Khz
  // Set Pins 9 & 10 (Timer1) frequency to 488.28125Hz or 31.25Khz
  //TCCR1B = TCCR1B & 0b11111000 | 0x04; // 488.28125Hz
  TCCR1B = TCCR1B & 0b11111000 | 0x01; // 31.25Khz
  // Set Pins 11 & 3 (Timer2) frequency to 488.28125Hz or 31.25Khz
  TCCR2B = TCCR2B & 0b11111000 | 0x04; // 488.28125Hz
  //TCCR2B = TCCR2B & 0b11111000 | 0x01; // 31.25Khz
  
  // declare the ledPin as an OUTPUT:
  pinMode(ledPin, OUTPUT);
  
  // turn the ledPin off
  digitalWrite(ledPin, LOW);

  // intialize the Serial Monitor
  if (DEBUG >= 1)
    Serial.begin(9600);

  // set default throttle value to neutral
  if (DEBUG > 1) {
    Serial.println("\nSetting Throttle Neutral");
    Serial.println("Setting Steering Neutral");
  }
  
  setPotentiometerValues(neutralValueThrottle, neutralValueSteering);

} // setup


void displayOutputValues() {
  // print debug information to console with throttle and steering values
  if (DEBUG > 1) {
    Serial.print("Throttle value: ");
    Serial.print("[PWM:");
    Serial.print(outputValueThrottle);
    Serial.print("] [");
    Serial.print(outputVoltageThrottle);
    Serial.println("V]");
    
    Serial.print("Steering value: ");
    Serial.print("[PWM:");
    Serial.print(outputValueSteering);
    Serial.print("] [");
    Serial.print(outputVoltageSteering);
    Serial.println("V]\n");
  }

} // displayOutputValues


void setPotentiometerValues(int throttle, int steering) {
  // set default throttle value to neutral
  outputValueThrottle = map(throttle, 0, 1023, 0, 255);
  outputVoltageThrottle = ((float)throttle / (float)1023 * 5);
  
  // set default steering value to neutral
  outputValueSteering = map(steering, 0, 1023, 0, 255);
  outputVoltageSteering = ((float)steering / (float)1023 * 5);

  displayOutputValues();
  
  analogWrite(outputPinThrottle, outputValueThrottle);
  analogWrite(outputPinSteering, outputValueSteering);
  
} // setPotentiometerValues


int readSerialInput(char delimiter) {
  // Drive RC Car by Serial input
  while(Serial.available() == 0); // pause until a byte is received by serial Rx
  inputByte = Serial.read();
  
  while(inputByte != delimiter) {
    while(Serial.available() == 0);
    inputByte = Serial.read();
  }
  
  while(Serial.available() == 0);
  inputByte = Serial.read();
  inputSign = inputByte;
  while(Serial.available() == 0);
  inputByte = Serial.read();
  inputValueString[0] = inputByte - 48; // ASCII conversion
  while(Serial.available() == 0);
  inputByte = Serial.read();
  inputValueString[1] = inputByte - 48;
  while(Serial.available() == 0);
  inputByte = Serial.read();
  inputValueString[2] = inputByte - 48;
  
  inputValue = int(inputValueString[0]) * 100 + \
               int(inputValueString[1]) * 10 + \
               int(inputValueString[2]);
  
  if (inputSign == '-')
    inputValue = -inputValue;
  
  return(inputValue);
  
} // readSerialInput


void updateRemoteControl() {
  // read control settings from serial input and set corresponding potentiometer values
  inputValue = readSerialInput(serialDelimiter);
  outputValueThrottle = calculateThrottlePower(inputValue);
  
  inputValue = readSerialInput(axisDelimiter);
  outputValueSteering = calculateSteeringPower(inputValue);
  
  setPotentiometerValues(outputValueThrottle, outputValueSteering);
  
} // updateRemoteControl


int calculateThrottlePower(int value) {
  // take a power input setting of 0 to 100 for forward or -100 to 0 for reverse
  if (value >=0) {
    ratio = (float)neutralValueThrottle / (float)forwardValue;
    value = int(ratio * (float)value);
    value = neutralValueThrottle + value;
  } else {
    ratio = (float)reverseValue / (float)neutralValueThrottle;
    value = -value;
    value = int(ratio * (float)value);
    value = neutralValueThrottle - value;
  }

  return(value);
  
} // calculateThrottlePower


int calculateSteeringPower(int value) {
  // take a power input setting of 0 to 100 for left or -100 to 0 for right
  if (value >=0) {
    ratio = (float)neutralValueSteering / (float)leftValue;
    value = int(ratio * (float)value);
    value = neutralValueSteering + value;
  } else {
    ratio = (float)rightValue / (float)neutralValueSteering;
    value = -value;
    value = int(ratio * (float)value);
    value = neutralValueSteering - value;
  }

  return(value);

} // calculateSteeringPower


int readAnalogSensor() {
  // read the value from the sensor:
  sensorValue = analogRead(sensorPin);
  
  // print the value from the sensor
  if (DEBUG > 1) {
    Serial.print("Input sensor value: ");
    Serial.println(sensorValue);
  }
  
  return(sensorValue);
  
} // readAnalogSensor


void readTestSensor() {
  // read the value from the sensor:
  testSensorValue = analogRead(testSensorPin);
  
  // print the value from the sensor
  if (DEBUG > 1) {
    Serial.print("Test sensor value: ");
    Serial.println(testSensorValue);
  }

} // readTestSensor


void writeoutputValueThrottle(int sensorValue) {
  // Map 10 bit (0 to 1023) analog input value to 8 bits (0 to 255)
  outputValueThrottle = map(sensorValue, 0, 1023, 0, 255);
  
  // print the PWM output value
  if (DEBUG > 1) {
    Serial.print("Output sensor value: ");
    Serial.println(outputValueThrottle);
  }
  
  // set the PWM output value for the output pin
  analogWrite(outputPinThrottle, outputValueThrottle);

} // writeoutputValueThrottle


void testDrive() {

  if (DEBUG > 1) {
    Serial.print("Drive value: ");
    Serial.print(forwardValue);
    Serial.println(" [Forward]");
  }
  
  outputValueThrottle = map(forwardValue, 0, 1023, 0, 255);
  analogWrite(outputPinThrottle, outputValueThrottle);
  digitalWrite(ledPin, HIGH);
  
  
  delay(2000);

  
  if (DEBUG > 1) {
    Serial.print("Drive value: ");
    Serial.print(neutralValueThrottle);
    Serial.println(" [Neutral]");
  }
  
  outputValueThrottle = map(neutralValueThrottle, 0, 1023, 0, 255);
  analogWrite(outputPinThrottle, outputValueThrottle);
  digitalWrite(ledPin, LOW);

} // testDrive


void driveRange() {
  
  delay(1000 * delayMultiplier);
  
  if (DEBUG > 1)
    Serial.println("Starting driveRange() loop\n");

  digitalWrite(ledPin, HIGH);
  
  for (int powerValue = neutralValueThrottle; powerValue <= forwardValue; powerValue++) {

    outputValueThrottle = map(powerValue, 0, 1023, 0, 255);
    //outputVoltageThrottle = map(powerValue, 0, 1023, 0, 5);
    outputVoltageThrottle = ((float)powerValue / (float)1023 * 5);

    if (DEBUG > 1) {
      //Serial.print("Delay Multipier: ");
      //Serial.println(delayMultiplier);
      //Serial.println();
      Serial.print("Drive value: ");
      Serial.print(powerValue);
      Serial.print(" [PWM:");
      Serial.print(outputValueThrottle);
      Serial.print("] [");
      Serial.print(outputVoltageThrottle);
      Serial.println("V]");
    }
    
    analogWrite(outputPinThrottle, outputValueThrottle);
    
    delay(100 * delayMultiplier);

  }   

  outputValueThrottle = map(neutralValueThrottle, 0, 1023, 0, 255);
  outputVoltageThrottle = ((float)neutralValueThrottle / (float)1023 * 5);
  if (DEBUG > 1) {
    Serial.println("\nSetting Neutral");
    Serial.print("Drive value: ");
    Serial.print(neutralValueThrottle);
    Serial.print(" [PWM:");
    Serial.print(outputValueThrottle);
    Serial.print("] [");
    Serial.print(outputVoltageThrottle);
    Serial.println("V]\n");
  }
  
  analogWrite(outputPinThrottle, outputValueThrottle);
  
  digitalWrite(ledPin, LOW);
   
} // driveRange


void loop() {

  //sensorValue = readAnalogSensor();
  
  //writeoutputValueThrottle(sensorValue);
  
  //readTestSensor();
  
  //testDrive();
  
  //driveRange();
  
  updateRemoteControl();
  
  // stop the program for for <delayValue> milliseconds:
  //if (DEBUG >= 1)
  //  delay(delayValue * delayMultiplier);
  
  // print an empty line between loops
  if (DEBUG > 1)
    Serial.println();
  
} // loop

