import serial
import numpy as np
import sys, os, math

class FernCL:
    def __init__(self):

        self.clPrint('fern-cl','Welcome to the Fern Command Line Interface...')
        self.clPrint('fern-cl','Type \'quit\' to exit the program at anytime...')
        
        # setup serial port
        self.arduinoPort = self.clInput('Enter the Arduino COM Port (e.g. "COM4"):')

        while not self.connectPort():
            self.clPrint('fern-cl','Invalid port.',error=True)
            self.arduinoPort = self.clInput('Enter Arduino COM Port (e.g. "COM4")...')

    def connectPort(self):
        if self.arduinoPort == 'DEBUG':
            return True
        try:
            s = serial.Serial(self.arduinoPort, 115200, timeout=1)
            s.close()
            return True
        except serial.serialutil.SerialException:
            return False

    @staticmethod
    def clPrint(origin,message,error=False):
        print('<{}> % {}{}'.format(origin.upper(),'ERROR: ' if error else '', message))

    @staticmethod
    def clInput(prompt):
        FernCL.clPrint('fern-cl',prompt)
        userInput = input('<USER> % ')

        if userInput == 'quit':
            FernCL.end()
        
        return userInput

    @staticmethod
    def end():
        FernCL.clPrint('fern-cl','Quitting...')
        sys.exit(0)

    def run(self):
        loop = True

        # main control loop
        while loop:
        
            instructionFile = self.clInput('Please enter the instruction file name...')

            while not os.path.exists(instructionFile):
                self.clInput('Please enter the instruction file name...')

            with open(instructionFile,'r') as f:
                with serial.Serial(self.arduinoPort, 115200, timeout=1) as s:
                
                    for line in f:
                        encodingList = self.parseLine(line)

                        for encoding in encodingList:

                            # wait for ready
                            while(s.read() != b'\x01'):
                                pass

                            # write
                            s.write(encoding)

                    # end in neutral position
                    while(s.read() != b'\x01'):
                        pass

                    # write
                    s.write(self.encodeRaise(1))

                    # end in neutral position
                    while(s.read() != b'\x01'):
                        pass

                    # write
                    s.write(self.encodeMove(150,50))

                    

    @staticmethod
    def parseLine(line):
        args = line.split(' ')
        cmd = args[0]

        # get list of instructions
        encodingList = []
        if cmd == 'M':
            x = float(args[1])
            y = float(args[2])
            encodingList.append(FernCL.encodeMove(x,y)) # move to location
        elif cmd == 'P':
            up = args[1] == '1'
            encodingList.append(FernCL.encodeRaise(up)) # raise/lower pen
        elif cmd == 'L':
            x1 = float(args[1])
            y1 = float(args[2])
            x2 = float(args[3])
            y2 = float(args[4])
            encodingList.append(FernCL.encodeRaise(1))              # raise pen
            encodingList.append(FernCL.encodeMove(x1,y1)) # move to starting point
            encodingList.append(FernCL.encodeRaise(0))              # lower pen
            encodingList.append(FernCL.encodeMove(x2,y2)) # move to finishing point
            encodingList.append(FernCL.encodeRaise(1))              # raise pen 
        elif cmd == 'R':
            x1 = float(args[1])
            y1 = float(args[2])
            x2 = float(args[3])
            y2 = float(args[4])
            encodingList.append(FernCL.encodeRaise(1))              # raise pen
            encodingList.append(FernCL.encodeMove(x1,y1)) # move to starting point
            encodingList.append(FernCL.encodeRaise(0))              # lower pen
            encodingList.append(FernCL.encodeMove(x1,y2)) # move to first corner
            encodingList.append(FernCL.encodeMove(x2,y2)) # move to second corner
            encodingList.append(FernCL.encodeMove(x2,y1)) # move to third corner
            encodingList.append(FernCL.encodeMove(x1,y1))
            encodingList.append(FernCL.encodeRaise(1))              # raise pen 
        elif cmd == 'C':
            xc = float(args[1])
            yc = float(args[2])
            r =  float(args[3])

            # go to starting point
            encodingList.append(FernCL.encodeRaise(1))
            encodingList.append(FernCL.encodeMove(xc+r,yc))
            encodingList.append(FernCL.encodeRaise(0))

            # draw circle 
            for theta in np.linspace(0,360,r*2):
                encodingList.append(FernCL.encodeMove(xc+r*math.cos(theta*math.pi/180), yc+r*math.sin(theta*math.pi/180)))
            
            encodingList.append(FernCL.encodeRaise(1))
        else:
            FernCL.clPrint('fern-cl','Invalid command',error=True)
            FernCL.end()

        return encodingList

    @staticmethod
    def encodeMove(x, y):
        return FernCL.encode(1,x*10,y*10) # encode in 100 micrometers

    @staticmethod
    def encodeRaise(up):
        return FernCL.encode(0,0,up)

    @staticmethod
    def encode(opcode,field1,field2):
        ''' Instruction set sent in 3 bytes:
        bit 0 -> blank
        bit 1 -> opcode: 0 for pen raise/lower, 1 for pen move
        bits 2-12 -> field 1: null for pen raise/lower, destination x (in steps) / 4 for pen move
        bits 13-23 -> field 2: null for pen raise/lower, destination y (in steps) / 4 for pen move
        '''
        
        return bytearray([int(opcode)& 0xFF, # opcode
                         (int(field1)>>8) & 0xFF, # 8 MSB field 1
                         int(field1) & 0xFF, # 8 LSB field 1
                         (int(field2)>>8) & 0xFF, # 8 MSB field 2
                         int(field2) & 0xFF]) # 8 LSB field 2

if __name__ == '__main__':
    f = FernCL()
    f.run()

