from abc import abstractmethod
import numpy as np
import sys, os, math

class FernWriter:

    def __init__(self, context):

        self.context = context
        self.send_move_instr
        self.pen_state = 1
        self.x_state = 0
        self.y_state = 0

        return None

    @abstractmethod
    def send_move_instr(self,x,y):
        pass

    @abstractmethod
    def send_pen_instr(self,new_pen_state):
        pass

    def parse_instr(self, instr):

        # parse
        fields = instr.split(' ')
        opcode = fields[0]
        args = [round(float(field),1) for field in fields[1:]]

        if opcode == 'M':
            x = args[0]
            y = args[1]
            self.send_move_instr(x, y)

        elif opcode == 'P':
            new_pen_state = int(fields[1])
            self.send_pen_instr(new_pen_state)

        elif opcode == 'L':
            x1 = args[0]
            y1 = args[1]
            x2 = args[2]
            y2 = args[3]
            self.send_line_instr(x1, y1, x2, y2)

        elif opcode == 'R':
            x1 = args[0]
            y1 = args[1]
            x2 = args[2]
            y2 = args[3]
            self.send_rect_instr(x1, y1, x2, y2)

        elif opcode == 'A':
            xc = args[0]
            yc = args[1]
            r = args[2]
            ts = args[3]
            te = args[4]
            self.send_arc_instr(xc, yc, r, ts, te)

        elif opcode == 'C':
            xc = args[0]
            yc = args[1]
            r = args[2]
            self.send_arc_instr(xc, yc, r, 0, 2*math.pi)

        return None

    def send_line_instr(self, x1, y1, x2, y2):
       
        self.send_pen_instr(1)
        self.send_move_instr(x1, y1)
        self.send_pen_instr(0)
        self.send_move_instr(x2, y2)

        return None

    def send_rect_instr(self, x1, y1, x2, y2):

        self.send_pen_instr(1) # raise 
        self.send_move_instr(x1, y1) # move
        self.send_pen_instr(0) # lower

        self.send_move_instr(x2, y2)

        return None

    def send_arc_instr(self, xc, yc, r, ts, te):

        self.send_pen_instr(1) # raise 
        self.send_move_instr(xc+r, yc) # move
        self.send_pen_instr(0) # lower
        
        # draw arc
        for theta in np.linspace(ts, te, r*5):
            self.send_move_instr(xc+r*math.cos(theta), yc+r*math.sin(theta))
        
        return None

    def draw(self, instruction_file):
        
        # allow serial or png file to initialize serial or svg file
        
        self.check_instruction_file(instruction_file)

        # open file
        with open(instruction_file,'r') as instructions:

            # get list of machine instructions
            for i, instr in enumerate(instructions):

                print(i, instr.strip())
                self.parse_instr(instr)
            # end raised 
            self.parse_instr('P 1')
            self.parse_instr('M 0 0')
            
        return None
        