#include <Servo.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

// pins
#define X_DIR_PIN 2
#define X_STEP_PIN 3
#define Y_DIR_PIN 4
#define Y_STEP_PIN 5
#define SERVO_PIN 6
#define X_BUMP_PIN 7
#define Y_BUMP_PIN 8

// parameters
#define INVERT_X_DIR true
#define INVERT_Y_DIR true
#define STEPPER_STEP_SIZE .04 // mm
#define STEPPER_MAX_SPEED 950 // steps/sec
#define SERVO_DELAY 500 // us
#define SERVO_ANGLE_UP 60 // deg
#define SERVO_ANGLE_DOWN 0 // deg
#define X_MAX 5000 // steps
#define Y_MAX 7500 // steps

class Fern{
  public:
  Fern(){
    
    // attach servo
    pen.attach(SERVO_PIN);
    raisePen();
    
    // instantiate motors
    xMotor = AccelStepper(AccelStepper::DRIVER,X_STEP_PIN,X_DIR_PIN);
    yMotor = AccelStepper(AccelStepper::DRIVER,Y_STEP_PIN,Y_DIR_PIN);

    // limit speed
    xMotor.setMaxSpeed(STEPPER_MAX_SPEED);
    yMotor.setMaxSpeed(STEPPER_MAX_SPEED);

    // invert pins (if necessary)
    xMotor.setPinsInverted(INVERT_X_DIR);
    yMotor.setPinsInverted(INVERT_Y_DIR);

    // attach motors
    if(!motors.addStepper(xMotor)){
      error();
    }
    if(!motors.addStepper(yMotor)){
      error();
    }     

    // calibration
    goHome();

    // initialize destination array
        
  }

  void raisePen(){
    if(!penState){
      pen.write(SERVO_ANGLE_UP);
      penState = HIGH;
      delayMicroseconds(SERVO_DELAY);
    }
  }

  void lowerPen(){
    if(penState){
      pen.write(SERVO_ANGLE_DOWN);
      penState = LOW;
      delayMicroseconds(SERVO_DELAY);
    }
  }

  void goHome(){
    raisePen();

    // reset orientation
    xMotor.setCurrentPosition(10000);
    yMotor.setCurrentPosition(0);

    long dest[2] = {0,0};

    // move x axis until bump
    motors.moveTo(dest);
    while(digitalRead(X_BUMP_PIN)){
      motors.run();
    }

    xMotor.setCurrentPosition(0);
    delay(1000);

    // move y axis until bump
    yMotor.setCurrentPosition(10000);
    motors.moveTo(dest);
    while(digitalRead(Y_BUMP_PIN)){
      motors.run();
    }

    yMotor.setCurrentPosition(0);
    delay(1000);
  }
  
  void movePenTo(int x, int y){

    // initialize dest
    long dest[2] = {x,y};
    Serial.println(dest[0]);
    Serial.println(dest[1]);
    motors.moveTo(dest);
    motors.runSpeedToPosition();
  }

  void parseSerial(){
    /* Instruction set sent in 3 bytes 
     * bit 0 -> blank
     * bit 1 -> opcode: 0 for pen raise/lower, 1 for pen move
     * bits 2-12 -> field 1: null for pen raise/lower, destination x (in mm) / .16 for pen move
     * bits 13-23 -> field 2: null for pen raise/lower, destination y (in mm) / .16 for pen move
     */

    Serial.write(1);
    
    int opcode;
    int field1;
    int field2;

    // opcode
    while(!Serial.available());
    opcode = Serial.read();
    
    // field 1 most significant byte
    while(!Serial.available());
    field1 = Serial.read();
    field1 <<= 8;

    // field 1 least significant byte
    while(!Serial.available());
    field1 += Serial.read();

    // field 2 most significant byte
    while(!Serial.available());
    field2 = Serial.read();
    field2 <<= 8;

    // field 2 least significant byte
    while(!Serial.available());
    field2 += Serial.read();
    
    // move 
    if(opcode){
      int x = field1 % X_MAX;
      int y = field2 % Y_MAX;

      movePenTo(x,y);
    }
    // pen
    else{
      if(field2){
        raisePen();
      }
      else{
        lowerPen();
      }
    }
  }

  private:
  void error(){
    while(1);
  }
  
  private:  
  Servo pen;
  AccelStepper xMotor;
  AccelStepper yMotor;
  MultiStepper motors;
  bool penState; // track pen state for some optimizations
};

void setup(){

  // serial setup
  Serial.begin(115200);
  
  // instantiate
  Fern f;

  while(1){
    f.parseSerial();
  }

}

void loop() {
 
}
