import serial
import sys
import argparse

from FernWriter import FernWriter

class FernWriterSerial(FernWriter):
	
	def send_move_instr(self,x,y):
		self.send_instr(self.get_move_instr(x,y))

		return None
	
	def send_pen_instr(self,new_pen_state):
		self.send_instr(self.get_pen_instr(new_pen_state))

		return None
                        
	def send_instr(self,instr):
		# wait for ready
		while not self.check_serial_ready():
			pass

		# write
		self.context.write(instr.encode('utf-8'))
		
		return None
		
	def check_serial_ready(self):
		return self.context.read() == 'R'.encode('utf-8')

	def format_float(self, n):
		return str(round(n,1)).zfill(5)

	def get_pen_instr(self, new_pen_state):
		return f"P {int(new_pen_state != 0)}0000 00000"

	def get_move_instr(self, x, y):
		return f"M {self.format_float(x)} {self.format_float(y)}"

def check_port(port):
	ser = serial.Serial()

	try:
		ser.port = port
		ser.baudrate = 115200
		ser.open()
	except serial.SerialException:
		sys.stderr.write(f"Bad port: {port}\n")
		sys.exit(1)

	ser.close()

	return None


def main(instruction_file, arduino_port):

	check_port(arduino_port)

	with serial.Serial(arduino_port, 115200, timeout=10) as ser:
		f = FernWriterSerial(ser)

		f.draw(instruction_file)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('instruction_file',type=str)
	parser.add_argument('arduino_port')

	args = parser.parse_args()

	main(args.instruction_file, args.arduino_port)
