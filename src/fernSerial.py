import serial
import time
import sys
import math

def main():
    # General meet and greet
    print('Welcome to the Fern Serial Interface!')

    # Port
    arduinoPort = input('Enter Arduino COM Port (e.g. "COM4") or type \"quit\" to exit: ')
    print('')

    if arduinoPort == 'quit': sys.exit(0)

    with serial.Serial(arduinoPort, 9600, timeout=1) as ser:
        time.sleep(2)

        # send circle
        xc = 20
        yc = 20
        r = 10

        # wait for ready
        status = ''
        while(status == ''):
            status = ser.readline().decode().replace('\n','')

        print(status)
        ser.write('m {} {}\n'.format(xc+r,yc).encode())
        

        # wait for ready

        status = ''
        while(status == ''):
            status = ser.readline().decode().replace('\n','')

        print(status)
        ser.write('p d\n'.encode())
        
        for i in range(360):

            # wait for ready
            status = ''
            while(status == ''):
                status = ser.readline().decode().replace('\n','')

            # send circle command 
            print(status)
            command = "m {:.1f} {:.1f}\n".format(xc+r*math.cos(i*math.pi/180.),yc+r*math.sin(i*math.pi/180.))
            ser.write(command.encode())   
            print(command)    
        

if __name__ == '__main__':
    main()

