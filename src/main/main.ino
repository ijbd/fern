#include <Servo.h>

// pins
#define X_DIR_PIN 2
#define X_STEP_PIN 3
#define Y_DIR_PIN 4
#define Y_STEP_PIN 5
#define SERVO_PIN 6
#define X_BUMP_PIN 7
#define Y_BUMP_PIN 8


// parameters
#define STEP_SIZE 4 // mm * 100
#define STEP_DELAY 600 // us
#define SERVO_DELAY 500 // us
#define SERVO_ANGLE_UP 140 // deg
#define SERVO_ANGLE_DOWN 80 // deg
#define X_MIN 0 // mm * 100
#define Y_MIN 0 // mm * 100
#define X_MAX 20000 // mm * 100
#define Y_MAX 30000 // mm * 100
#define STEP_BUFFER_CAPACITY 200 
#define INSTR_BUFFER_CAPACITY 100

// serial codes
#define SERIAL_READY 1
#define SERIAL_ERROR_BAD_INSTR 2

// other macros for readability
#define FORWARD 0
#define REVERSE 1


class Fern{
  // Public Functions
  public:
    Fern(){
      // Attach pen
      pen.attach(SERVO_PIN);
      delay(1000);

      // Lift pen
      penUp();

      // Go home
      moveHome();

      // Allocate buffer space
      xStepBuffer = new bool[STEP_BUFFER_CAPACITY];
      yStepBuffer = new bool[STEP_BUFFER_CAPACITY];
      stepBufferSize = 0;

      // Send ready
      Serial.write(SERIAL_READY);
    }

    ~Fern(){
      penUp();
      moveTo(0,30);
      moveTo(30,30);
      delete[] xStepBuffer;
      delete[] yStepBuffer;
    }

    void parseInstruction(){
      int opcode;
      int arg0;
      int arg1;
      
      // wait for instruction
      while(Serial.available() < 5);

      // get opcode
      opcode = Serial.read();

      // get arg0
      for(int i = 0; i<2; ++i){
        arg0 <<= 8;
        arg0 |= Serial.read();
      }

      // get arg1
      for(int i = 0; i<2; ++i){
        arg1 <<= 8;
        arg1 |= Serial.read();
      }

      Serial.write(SERIAL_READY);

      // Decode and execute
      switch(opcode){
        case 0: // pen
          if(arg1 == 1) penUp();
          else penDown();
          break;
        case 1: // move
          moveTo(arg0,arg1);
          break;
        default:
          error(SERIAL_ERROR_BAD_INSTR);
      }
    }

    void penUp(){
      pen.write(SERVO_ANGLE_UP);
      delayMicroseconds(SERVO_DELAY);
    }

    void penDown(){
      pen.write(SERVO_ANGLE_DOWN);
      delayMicroseconds(SERVO_DELAY);
    }

    void moveTo(double xDest, double yDest){
      xDest = min(max(xDest,X_MIN),X_MAX);
      yDest = min(max(yDest,Y_MIN),Y_MAX);

      // Initialize Bessenham variables
      int x0 = int(x/STEP_SIZE);
      int x1 = int(xDest/STEP_SIZE);
      int y0 = int(y/STEP_SIZE);
      int y1 = int(yDest/STEP_SIZE);
      
      xDir = (x1 >= x0);
      yDir = (y1 >= y0);
      
      // Begin Bessenham algorithm
      if(abs(y1 - y0) < abs(x1 - x0)){
        if(!xDir){          
          plotLineLow(x1, y1, x0, y0);
        }
        else{
          plotLineLow(x0, y0, x1, y1);
        }
      }
      else{
        if(!yDir){
          plotLineHigh(x1, y1, x0, y0);
        }
        else{
          plotLineHigh(x0, y0, x1, y1);
        }
      }
       
      moveMotors();
    }
  
  // Private Functions
  private:

    void error(int errorCode){
      Serial.write(errorCode);
      while(1);
    }
  
    void moveHome(){
      // Go to x-zero
      digitalWrite(X_DIR_PIN,REVERSE);
      delayMicroseconds(STEP_DELAY);
      
      while(digitalRead(X_BUMP_PIN)){
        digitalWrite(X_STEP_PIN,HIGH);
        delayMicroseconds(STEP_DELAY);
        digitalWrite(X_STEP_PIN,LOW);
        delayMicroseconds(STEP_DELAY);
      }

      // Go to y-zero
      digitalWrite(Y_DIR_PIN,REVERSE);
      delayMicroseconds(STEP_DELAY);
      
      while(digitalRead(Y_BUMP_PIN)){
        digitalWrite(Y_STEP_PIN,HIGH);
        delayMicroseconds(STEP_DELAY);
        digitalWrite(Y_STEP_PIN,LOW);
        delayMicroseconds(STEP_DELAY);
      }

      // set postion
      x = 0;
      y = 0;
    }

    void moveMotors(){

      // Set direction
      double dx = (xDir) ? STEP_SIZE : -STEP_SIZE;
      double dy = (yDir) ? STEP_SIZE : -STEP_SIZE;
      digitalWrite(X_DIR_PIN,(xDir) ? FORWARD : REVERSE);
      digitalWrite(Y_DIR_PIN,(yDir) ? FORWARD : REVERSE);

      delayMicroseconds(STEP_DELAY);

      // step
      for(int i = 0; i < stepBufferSize; ++i){

        // check x
        if(xStepBuffer[i]){
          digitalWrite(X_STEP_PIN,HIGH);
          x += dx;
          delayMicroseconds(STEP_DELAY);
          digitalWrite(X_STEP_PIN,LOW);
          delayMicroseconds(STEP_DELAY);
        }

        // check y
        if(yStepBuffer[i]){
          digitalWrite(Y_STEP_PIN,HIGH);
          y += dy;
          delayMicroseconds(STEP_DELAY);
          digitalWrite(Y_STEP_PIN,LOW);
          delayMicroseconds(STEP_DELAY);
        }

      }

      // reset buffer
      stepBufferSize = 0;
    }

    // Bessenham Algorithm
    void plotLineLow(int x0, int y0, int x1, int y1){
      int dx = x1 - x0;
      int dy = y1 - y0;
      int yi = 1;
      
      if(dy < 0){
        yi = -1;
        dy = -dy;
      }
      
      int D = (2 * dy) - dx;
      int y_c = y0;
      
      for(int x_c = x0; x_c < x1; x_c++){
        if(D > 0){
          y_c += yi;
          D = D + (2 * (dy - dx));
          yStepBuffer[stepBufferSize] = 1;
        }
        else{
          D = D + 2*dy;
          yStepBuffer[stepBufferSize] = 0;
        }

        // step buffers
          xStepBuffer[stepBufferSize++] = 1;

        if(stepBufferSize == STEP_BUFFER_CAPACITY){
          moveMotors();
        }
      }
    }

    // Bessenham Algorithm
    void plotLineHigh(int x0, int y0, int x1, int y1){
      int dx = x1 - x0;
      int dy = y1 - y0;
      int xi = 1;
      if(dx < 0){
          xi = -1;
          dx = -dx;
      }
      int D = (2 * dx) - dy;
      int x_c = x0;
  
      for(int y_c = y0; y_c < y1; y_c++){
        if(D > 0){
          x_c += xi;
          D = D + (2 * (dx - dy));
          xStepBuffer[stepBufferSize] = 1;
        }
        else{
          D = D + 2*dx;
          xStepBuffer[stepBufferSize] = 0;
        }

        // always step y
        yStepBuffer[stepBufferSize++] = 1;

        if(stepBufferSize == STEP_BUFFER_CAPACITY){
          moveMotors();
        }
      }
    }
    
    Servo pen; 
    double x;
    double y;
    int stepBufferSize;
    bool * xStepBuffer;
    bool * yStepBuffer;
    bool xDir;
    bool yDir;
      
};

void setup() {

  // Serial 
  Serial.begin(115200);
  while(!Serial);

  // Inputs
  pinMode(X_BUMP_PIN, INPUT);
  pinMode(Y_BUMP_PIN, INPUT);
  
  // Outputs
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  
  // Instantiate
  Fern f;

  bool dir = FORWARD;
  while(1){
    delay(1000);

    digitalWrite(X_DIR_PIN, dir);
    digitalWrite(Y_DIR_PIN, dir);
    delayMicroseconds(STEP_DELAY);
    
    for(int i = 0; i < 1000; ++i){
        digitalWrite(X_STEP_PIN,HIGH);
        delayMicroseconds(STEP_DELAY);
        digitalWrite(X_STEP_PIN,LOW);
        delayMicroseconds(STEP_DELAY);
    }

    dir = !dir;
  }

  while(1){
    f.parseInstruction();
  }
}


void loop() {

}
