#include <AccelStepper.h>    //Utiliza la libreria AccelStepper

// Variables rediseño
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

//Variablesdel sistema
int baudios = 9600;            //9600 //19200
float velocidadMax = 600.0;    //(666 max) maximum steps per second
float motorAccel = 6000.0;     //steps/second/second to accelerate
int pasosVuelta = 200;     //Numero de pasos para dar una vuelta del motor
// Pines para motores
int motorXDirPin = 2;  //digital pin 2
int motorXStepPin = 3; //digital pin 3
int resetX = 8;      //Motor X
int motorYDirPin = 4;  //digital pin 4
int motorYStepPin = 5; //digital pin 5
int resetY = 9;      //Motor X
int motorZDirPin = 6;  //digital pin 6
int motorZStepPin = 7; //digital pin 7
int resetZ = 10;      //Motor X

//set up the accelStepper intances
AccelStepper stepperX(1, motorXStepPin, motorXDirPin); //the "1" tells it we are using a driver
AccelStepper stepperY(1, motorYStepPin, motorYDirPin);
AccelStepper stepperZ(1, motorZStepPin, motorZDirPin);

// Pines para botones limite
const int buttonPinX1 = 8;      // the number of the pushbutton pin
const int buttonPinX2 = 9;      // the number of the pushbutton pin
const int buttonPinY1 = 10;     // the number of the pushbutton pin
const int buttonPinY2 = 11;     // the number of the pushbutton pin
const int buttonPinZ1 = 12;     // the number of the pushbutton pin
const int buttonPinZ2 = 13;     // the number of the pushbutton pin

// Constantes para leer el estado de los botones
int buttonState = 0;                           // variable for reading the pushbutton status

void setup(){
  // Set reset pins
  stepperX.setEnablePin(resetX);
  stepperY.setEnablePin(resetY);
  stepperZ.setEnablePin(resetZ);
  
  // Set maximun speeds
  stepperX.setMaxSpeed(velocidadMax);
  stepperY.setMaxSpeed(velocidadMax);
  stepperZ.setMaxSpeed(velocidadMax);
  
  // Set accelerations
  stepperX.setAcceleration(motorAccel);
  stepperY.setAcceleration(motorAccel);
  stepperZ.setAcceleration(motorAccel);
  
  // Initialize the pushbutton pins as inputs
  pinMode(buttonPinX1, INPUT);   
  pinMode(buttonPinX2, INPUT);
  pinMode(buttonPinY1, INPUT);
  pinMode(buttonPinY2, INPUT);
  pinMode(buttonPinZ1, INPUT);
  pinMode(buttonPinZ2, INPUT);
  
  stepperX.enableOutputs();
  stepperY.enableOutputs();
  stepperZ.enableOutputs();
  
  stepperX.disableOutputs();
  stepperY.disableOutputs();
  stepperZ.disableOutputs();
  
  // Initialize serial port
  Serial.begin(baudios);       // initialize serial
  //inputString.reserve(200);    // reserve 200 bytes for the inputString
  /*
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }*/

  // send an intro:
  Serial.println("Conectado");
  //delay(2000);
}

void loop() {
  // serial
  // Comienza el rediseño
  if (stringComplete) {
    if (inputString.startsWith("M1")){
        //Serial.println("Moviendo CNC");
        compruebaOrden(inputString);
    }
    if (inputString.startsWith("STOP")){   
        Serial.println("CNC parada"); 
    }
    if (inputString.startsWith("CHECK")){   
        Serial.println("OK"); 
    }else{
        Serial.println("Orden no reconocida");
    }// Finish the conditional for M1 or STOP or else    
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}

int* compruebaOrden(String orden){                                 //Comprueba que la orden tenga todos los parametros
  int indiceX = orden.indexOf("X");                                 //La variable indiceX almacena la posicion donde comenzar la orden para el motor M1.
  int indiceY = orden.indexOf("Y");                                 //La variable indiceY almacena la posicion donde comenzar la orden para el motor M2.
  int indiceZ = orden.indexOf("Z");                                 //La variable indiceZ almacena la posicion donde comenzar la orden para el motor M3.
  int indiceU = orden.indexOf("U");                                 //La variable indiceU almacena la velocidad para el motor M1.
  int indiceV = orden.indexOf("V");                                 //La variable indiceZ almacena la velocidadn para el motor M2.
  int indiceW = orden.indexOf("W");                                 //La variable indiceZ almacena la velocidad para el motor M3.

  int longitud = orden.length();                                    // Obtains the length of the array

  int nuevaOrden[6];                                                //Crea el array de floats que almacenara las coordenadas y velocidades
  nuevaOrden[0] = (orden.substring(indiceX+1, indiceY)).toInt();    //Pasa la subcadena entre los indices X e Y, los convierte a int, luego a float y los almacena en el array
  nuevaOrden[1] = (orden.substring(indiceY+1, indiceZ)).toInt();
  nuevaOrden[2] = (orden.substring(indiceZ+1, indiceU)).toInt();
  nuevaOrden[3] = (orden.substring(indiceU+1, indiceV)).toInt();
  nuevaOrden[4] = (orden.substring(indiceV+1, indiceW)).toInt();
  nuevaOrden[5] = (orden.substring(indiceW+1, longitud)).toInt();

  mueve_motores(nuevaOrden);                                         // Executes the function that moves the motors with the values obteined

  return nuevaOrden;                                                 //Devuelve el array con los int (coordenadas y velocidades)
}

void mueve_motores(int* ordenes_mueve){                         //Comprueba que la orden tenga todos los parametros

  const long stepsX = ordenes_mueve[0];          // Asigns the firts value of the array to the X steps
  const float speedX = ordenes_mueve[3];
  const long stepsY = ordenes_mueve[1];
  const float speedY = ordenes_mueve[4];
  const long stepsZ = ordenes_mueve[2];
  const float speedZ = ordenes_mueve[5];
  
  stepperX.move(stepsX);        // Amount of steps to move (move 200 steps (should be 1 rev))
  stepperX.setSpeed(speedX);    // Speed of the motor when moving      
  stepperY.move(stepsY);        // Amount of steps to move (move 200 steps (should be 1 rev))
  stepperY.setSpeed(speedY);      
  stepperZ.move(stepsZ);        // Amount of steps to move (move 200 steps (should be 1 rev))
  stepperZ.setSpeed(speedZ);

  long posicionInicialX = stepperX.currentPosition();
  long posicionInicialY = stepperY.currentPosition();
  long posicionInicialZ = stepperZ.currentPosition();

  if (speedX != 0){
      stepperX.enableOutputs();
      if (speedX > 0){
          while (stepperX.currentPosition() != posicionInicialX + stepsX) { // check if the metro has passed its interval .
              stepperX.runSpeed();
              if (speedY != 0){
                  stepperY.enableOutputs();
                  stepperY.runSpeed();
              }
              if (speedZ != 0){
                  stepperZ.enableOutputs();
                  stepperZ.runSpeed();
              }
            }
        }else{
            while (stepperX.currentPosition() != posicionInicialX - stepsX) { // check if the metro has passed its interval .
              stepperX.runSpeed();
              if (speedY != 0){
                stepperY.enableOutputs();
                stepperY.runSpeed();
              }
              if (speedZ != 0){
                stepperZ.enableOutputs();
                stepperZ.runSpeed();
              }
            }
        }
        stepperX.disableOutputs();
        stepperY.disableOutputs();
        stepperZ.disableOutputs();
    }else if (speedY != 0){
        stepperY.enableOutputs();
        if (speedY > 0){
            while (stepperY.currentPosition() != posicionInicialY + stepsY) { // check if the metro has passed its interval .
              //stepperX.runSpeed();
              stepperY.runSpeed();
              if (speedZ != 0){
                stepperZ.enableOutputs();
                stepperZ.runSpeed();
              }
            }
        }else{
            while (stepperY.currentPosition() != posicionInicialY - stepsY) { // check if the metro has passed its interval .
              //stepperX.runSpeed();
              stepperY.runSpeed();
              if (speedZ != 0){
                stepperZ.enableOutputs();
                stepperZ.runSpeed();
              }
            }
        }
        stepperY.disableOutputs();
        stepperZ.disableOutputs();
    }else{
        stepperZ.enableOutputs();
        if (speedZ > 0){
            while (stepperZ.currentPosition() != posicionInicialZ + stepsZ) { // check if the metro has passed its interval .
              //stepperX.runSpeed();
              //stepperY.runSpeed();
              stepperZ.runSpeed();
            }
        }else{
            while (stepperZ.currentPosition() != posicionInicialZ - stepsZ) { // check if the metro has passed its interval .
              //stepperX.runSpeed();
              //stepperY.runSpeed();
              stepperZ.runSpeed();
            }
        }
        stepperZ.disableOutputs();
    }
    //Serial.flush();
    Serial.println("OK"); // Returns OK after moving the motors
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available()) {
    
    // get the new byte:
    char inChar = (char)Serial.read(); 
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
