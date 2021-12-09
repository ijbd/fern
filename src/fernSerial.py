import serial
import time
import sys
import math


def encodePen(up):
    return bytearray([0,0,0,0,up])

def encodeMove(x,y):
    arg0 = int(x*100)
    arg1 = int(y*100)
    return bytearray([1,(arg0>>8),(arg0&0xff),(arg1>>8),(arg1&0xff)])

def main():
    # General meet and greet
    print('Welcome to the Fern Serial Interface!')

    # Port
    arduinoPort = input('Enter Arduino COM Port (e.g. "COM4") or type \"quit\" to exit: ')
    print('')

    if arduinoPort == 'quit': sys.exit(0)

    with serial.Serial(arduinoPort, 115200, timeout=1) as ser:
        time.sleep(2)

        # wait for ready
        while(ser.read() == ''):
            None

        # draw a circle
        xc = 60
        yc = 60
        r = 25

        ser.write(encodeMove(xc+r,yc))
            
        while not ser.in_waiting:
            None

        ser.write(encodePen(0))
            
        while not ser.in_waiting:
            None

        for i in range(360):
    
            ser.write(encodeMove(xc+r*math.cos(i/180.*3.14),yc+r*math.sin(i/180.*3.14)))
            
            while not ser.in_waiting:
                None
                 

if __name__ == '__main__':
    main()

