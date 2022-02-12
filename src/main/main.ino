/* Fern
 * ~~~~~~~~~~~
 * Code by ijbd
 */

// includes
#include <Servo.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

// defines
#define MOTOR_A_DIR_PIN 2
#define MOTOR_A_STEP_PIN 3
#define MOTOR_A_MS_1_PIN 5
#define MOTOR_A_MS_2_PIN 4
#define MOTOR_A_INVERT false
#define MOTOR_B_DIR_PIN 6
#define MOTOR_B_STEP_PIN 7
#define MOTOR_B_MS_1_PIN 9
#define MOTOR_B_MS_2_PIN 8
#define MOTOR_B_INVERT false
#define SERVO_PIN 10
#define SERVO_ANGLE_DOWN 0
#define SERVO_ANGLE_UP 30
#define SERVO_DELAY 1500
#define BUMPER_X_PIN 11
#define BUMPER_Y_PIN 12
#define STEP_MAX_SPEED 600 
#define STEPS_PER_MM 50 
#define X_LIM_STEPS 12500
#define Y_LIM_STEPS 15000

// struct
class Fern{
public:
  Fern():pen(),motor_a(),motor_b(),motors(),pen_state(0){
    // attach servo
    pen.attach(SERVO_PIN);

    // init motors
    init_motors();

    // go home
    go_home();
  }

  void init_motors(){
    
    // instantiate motors
    motor_a = AccelStepper(AccelStepper::DRIVER,MOTOR_A_STEP_PIN, MOTOR_A_DIR_PIN);
    motor_b = AccelStepper(AccelStepper::DRIVER,MOTOR_B_STEP_PIN, MOTOR_B_DIR_PIN);
  
    // set microstep pins
    digitalWrite(MOTOR_A_MS_1_PIN, HIGH);
    digitalWrite(MOTOR_A_MS_2_PIN, HIGH);
    digitalWrite(MOTOR_B_MS_1_PIN, HIGH);
    digitalWrite(MOTOR_B_MS_2_PIN, HIGH);
  
    // limit speed
    motor_a.setMaxSpeed(STEP_MAX_SPEED);
    motor_b.setMaxSpeed(STEP_MAX_SPEED);
  
    // invert pins if necessery
    motor_a.setPinsInverted(MOTOR_A_INVERT);
    motor_b.setPinsInverted(MOTOR_B_INVERT);
  
    // add motor
    motors.addStepper(motor_a);
    motors.addStepper(motor_b);
  }

  void go_home(){
    
    // lift 
    raise_pen();
    
    // find x = 0
    while(digitalRead(BUMPER_X_PIN)){
      motor_a.setSpeed(-STEP_MAX_SPEED);
      motor_a.runSpeed();   
      motor_b.setSpeed(-STEP_MAX_SPEED);
      motor_b.runSpeed();   
    }
    
    // find y = 0
    while(digitalRead(BUMPER_Y_PIN)){
      motor_a.setSpeed(STEP_MAX_SPEED);
      motor_a.runSpeed();
      motor_b.setSpeed(-STEP_MAX_SPEED);
      motor_b.runSpeed();
    }
   
    // set position
    motor_a.setCurrentPosition(0);
    motor_b.setCurrentPosition(0);
  }

  void move_to(int x, int y){
    
    // rotate x/y into a/b coordinate system
    long dest[2];
    
    dest[0] = .707*(x-y);
    dest[1] = .707*(x+y);

    motors.moveTo(dest);
    motors.runSpeedToPosition();
  }

  void raise_pen(){
    if(!pen_state){
      pen.write(SERVO_ANGLE_UP);
      pen_state = HIGH;
      delayMicroseconds(SERVO_DELAY);
    }
  }

  void lower_pen(){
    if(pen_state){
      pen.write(SERVO_ANGLE_DOWN);
      pen_state = LOW;
      delayMicroseconds(SERVO_DELAY);
    }
  }

  void parse_serial(){

    // send ready
    //Serial.write('R');
    
    // wait for incoming command 
    while(!Serial.available());

    // read opcode
    char opcode = Serial.read();
    
    switch(opcode){
      case 'M':
        parse_move();
        break;
      case 'P':
        parse_pen();
        break;
    }
  }

  void parse_move(){

    // read arguments
    float x_mm_dest = Serial.parseFloat();
    float y_mm_dest = Serial.parseFloat();

    // convert to steps
    int x_dest = x_mm_dest * STEPS_PER_MM;
    int y_dest = y_mm_dest * STEPS_PER_MM;

    // limit check
    x_dest = min(X_LIM_STEPS, max(x_dest, 0));
    y_dest = min(Y_LIM_STEPS, max(y_dest, 0));

    // move 
    move_to(x_dest,y_dest); 
         
  }

  void parse_pen(){

    // read argument
    int pen_state_dest= Serial.parseInt();

    if(pen_state_dest){
      raise_pen();
    }
    else{
      lower_pen();
    }
  }
  
private:
  Servo pen;
  AccelStepper motor_a;
  AccelStepper motor_b;
  MultiStepper motors;
  int pen_state;
};

void pin_setup(){
  pinMode(MOTOR_A_STEP_PIN, OUTPUT);
  pinMode(MOTOR_A_DIR_PIN, OUTPUT);
  pinMode(MOTOR_A_MS_1_PIN, OUTPUT);
  pinMode(MOTOR_A_MS_2_PIN, OUTPUT);

  pinMode(MOTOR_B_STEP_PIN, OUTPUT);
  pinMode(MOTOR_B_DIR_PIN, OUTPUT);
  pinMode(MOTOR_B_MS_1_PIN, OUTPUT);
  pinMode(MOTOR_B_MS_2_PIN, OUTPUT);

  pinMode(SERVO_PIN, OUTPUT);
}

void setup(){
  Serial.begin(115200);

  pin_setup();

  Fern f;

  while(1){
    f.parse_serial();
  }
}

void loop() {
  
}
