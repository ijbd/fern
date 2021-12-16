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
#define INVERT_X_DIR false
#define INVERT_Y_DIR false
#define STEPPER_STEP_SIZE .04 // mm
#define STEPPER_MAX_SPEED 1200
#define SERVO_DELAY 500 // us
#define SERVO_ANGLE_UP 60 // deg
#define SERVO_ANGLE_DOWN 0 // deg
#define X_MIN 0 // steps
#define Y_MIN 0 // steps
#define X_MAX 5000 // steps
#define Y_MAX 7500 // steps

class Fern{
  public:
  Fern(){
    Serial.println("%% Instantiating Fern...");

    // attach servo
    pen.attach(SERVO_PIN);
    penUp();
    
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
      Serial.println("%% ERROR: Failed to attach x motor.");
      error();
    }
    if(!motors.addStepper(yMotor)){
      Serial.println("%% ERROR: Failed to attach y motor.");
      error();
    }     

    // calibration
    goHome();

    // initialize destination array
        
  }

  void penUp(){
    if(!penState){
      pen.write(SERVO_ANGLE_UP);
      penState = HIGH;
      delayMicroseconds(SERVO_DELAY);
    }
  }

  void penDown(){
    if(penState){
      pen.write(SERVO_ANGLE_DOWN);
      penState = LOW;
      delayMicroseconds(SERVO_DELAY);
    }
  }

  void goHome(){
    penUp();
    
    while(LOW && digitalRead(X_BUMP_PIN)){
      xMotor.move(-1);
      while(xMotor.run());
    }

    xMotor.setCurrentPosition(0);
    delay(1000);

    while(LOW && digitalRead(Y_BUMP_PIN)){
      yMotor.move(-1);
      while(yMotor.run());
    }

    yMotor.setCurrentPosition(0);
    delay(1000);

    Serial.println("%% Found home position...");
  }
  
  void moveToPos(int x, int y){
    Serial.println("%% Moving to position...");

    // initialize dest
    long dest[2] = {x,y};
    Serial.println(dest[0]);
    Serial.println(dest[1]);
    motors.moveTo(dest);
    while(motors.run());
  }

  void rect(int x1, int y1, int x2, int y2){

    Serial.println("%% Drawing rectangle...");
    
    // if current position is not starting position, raise pen and move
    if(x1 != xMotor.currentPosition() || y1 != yMotor.currentPosition()){
      penUp();
      moveToPos(x1,y1);
      penDown();
    }

    // draw rectangle
    moveToPos(x1,y2);
    moveToPos(x2,y2);
    moveToPos(x2,y1);
    moveToPos(x1,y1);
     
  }

  void line(int x1, int y1, int x2, int y2){
    
    Serial.println("%% Drawing line...");
    
    // if current position is not starting position, raise pen and move
    if(x1 != xMotor.currentPosition() || y1 != yMotor.currentPosition()){
      penUp();
      moveToPos(x1,y1);
      penDown();
    }

    // draw line
    moveToPos(x2,y2);
  }

  void circle(int xc, int yc, int r){

    Serial.println("%% Drawing circle...");

    // if current position is not starting position, raise pen and move
    if(xc+r != xMotor.currentPosition() || yc != yMotor.currentPosition()){
      penUp();
      moveToPos(xc,yc);
      penDown();
    }

    // draw circle
    int * x = new int[100];
    int * y = new int[100];
    for(int theta = 0; theta < 100; ++theta){
       x[theta] = xc+r*cos(theta/180*3.14);
       y[theta] = yc+r*sin(theta/180*3.14);
    }
  }

  private:

  int mmToSteps(double mm){
    return mm/STEPPER_STEP_SIZE;
  }
  
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
    f.rect(0,0,300,300);
    delay(1000);

    f.circle(100,100,50);
    delay(1000);
  }
}

void loop() {
 
}
