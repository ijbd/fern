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
#define STEP_SIZE .04
#define STEP_DELAY 600
#define SERVO_DELAY 500
#define SERVO_ANGLE_UP 140
#define SERVO_ANGLE_DOWN 80
#define X_MIN 0
#define Y_MIN 0
#define X_MAX 200
#define Y_MAX 300
#define STEP_BUFFER_CAPACITY 200

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
      Serial.println(SERIAL_READY);
    }

    ~Fern(){
      penUp();
      moveTo(0,30);
      moveTo(30,30);
      delete[] xStepBuffer;
      delete[] yStepBuffer;
    }

    void parseInstruction(){
      String sdata = "";
      byte ch;
      bool received = false;

      // Read in command
      while(!received){
        if(Serial.available() > 0){
          ch = Serial.read();

          sdata += (char)ch;

          if(ch == '\n'){
            received = true;   
          }
          else if(sdata.length() >= 32){
            error(SERIAL_ERROR_BAD_INSTR);
          }
        }      
      }

      //Serial.println(SERIAL_READY);

      // Decode and execute
      switch((char) sdata.charAt(0)){
        case 'm':
          parseMove(sdata);
          break;
        case 'p':
          parsePen(sdata);
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

    void parseMove(String &instr){
      // error handling and tokenizing
      if(instr.charAt(1) != ' ') error(SERIAL_ERROR_BAD_INSTR);
      int i = 2; 
      while(instr.charAt(i) != ' ' && i < instr.length()) i++;
      if(i >= instr.length()-1) error(SERIAL_ERROR_BAD_INSTR);

      // get args
      double xDest = instr.substring(2,i).toDouble();
      double yDest = instr.substring(i+1).toDouble();

      Serial.print("Move to ");
      Serial.print(xDest);
      Serial.print(' ');
      Serial.println(yDest);
      moveTo(xDest,yDest);
    }
    
    void parsePen(String &instr){
      // error handling and tokenizing
      if(instr.charAt(1) != ' ') error(SERIAL_ERROR_BAD_INSTR);
      if(instr.charAt(3) != '\n') error(SERIAL_ERROR_BAD_INSTR);

      // get arg and execute
      switch(instr.charAt(2)){
        case 'u':
          Serial.println("Pen up!");
          penUp();
          break;
        case 'd':
          Serial.println("Pen up!");
          penDown();
          break;
        default:
          error(SERIAL_ERROR_BAD_INSTR);
      }  
    }
    
    void error(int errorCode){
      Serial.println(errorCode);
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
        }

        // check y
        if(yStepBuffer[i]){
          digitalWrite(Y_STEP_PIN,HIGH);
          y += dy;
        }

        // end step
        delayMicroseconds(STEP_DELAY);
        digitalWrite(X_STEP_PIN,LOW);
        digitalWrite(Y_STEP_PIN,LOW);
        delayMicroseconds(STEP_DELAY);
        
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
  
  // Instantiate
  Fern f;

  while(1){
    f.parseInstruction();
  }
}


void loop() {

}
