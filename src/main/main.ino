#include <Servo.h>

// pins
#define X_STEP_PIN 0
#define X_DIR_PIN 1
#define Y_STEP_PIN 2
#define Y_DIR_PIN 3
#define X_BUMP_PIN 4
#define Y_BUMP_PIN 5
#define SERVO_PIN 6

// parameters
#define STEP_SIZE .04444
#define STEP_DELAY 1500
#define SERVO_DELAY 100
#define SERVO_UP_ANGLE 130
#define SERVO_DOWN_ANGLE 80
#define X_MIN 0
#define Y_MIN 0
#define X_MAX_CM 203.2
#define Y_MAX_CM 304.8
#define STEP_BUFFER_CAPACITY 10000

// other macros for readability
#define FORWARD 1
#define REVERSE 0

class Fern{
  // Public Functions
  public:
    Fern(){
      pen.attach(SERVO_PIN);
      stepBuffer = new bool[STEP_BUFFER_CAPACITY];
      stepBufferSize = 0;
    }

    void testBumpers(){
      Serial.println("Testing bumpers...");
      while(
      
    }

    void testMotors(){
      Serial.println("Testing steppers...");
      
      // test motors
      digitalWrite(X_DIR_PIN,FORWARD);
      digitalWrite(Y_DIR_PIN,FORWARD);
      delayMicroseconds(STEP_DELAY);

      Serial.println("X forward...");
      for(int i = 0; i < 200; ++i){
        digitalWrite(X_STEP_PIN,HIGH);
        delayMicroseconds(STEP_DELAY);
        digitalWrite(X_STEP_PIN,LOW);
        delayMicroseconds(STEP_DELAY);
      }

      delay(2000);

      Serial.println("Y forward...");
      for(int i = 0; i < 200; ++i){
        digitalWrite(Y_STEP_PIN,HIGH);
        delayMicroseconds(STEP_DELAY);
        digitalWrite(Y_STEP_PIN,LOW);
        delayMicroseconds(STEP_DELAY);
      }

      delay(2000);

      digitalWrite(X_DIR_PIN,REVERSE);
      digitalWrite(Y_DIR_PIN,REVERSE);
      delayMicroseconds(STEP_DELAY);

      Serial.println("Both reverse...");
      for(int i = 0; i < 200; ++i){
        digitalWrite(X_STEP_PIN,HIGH);
        digitalWrite(Y_STEP_PIN,HIGH);
        delayMicroseconds(STEP_DELAY);
        digitalWrite(X_STEP_PIN,LOW);
        digitalWrite(Y_STEP_PIN,LOW);
        delayMicroseconds(STEP_DELAY);
      }
    }
  
  // Private Functions
  private:

  // Public Variables
  public:

  // Private Variables
  private:
    Servo pen; 
    
      
};

void setup() {

  // Serial 
  Serial.begin(9600);
  while(!Serial);

  // Inputs
  pinMode(X_BUMP_PIN, INPUT);
  pinMode(Y_BUMP_PIN, INPUT);
  
  // Outputs
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(SERVO_PIN, OUTPUT);
  
  // Instantiate
  delay(3000);
  Fern f;
  
  // run
  f.testMotors();
}


void loop() {

}
