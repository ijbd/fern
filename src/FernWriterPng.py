import serial
import sys
import argparse
import cairo
import os

from FernWriter import FernWriter

PEN_WIDTH = .5
FERN_WIDTH = 250
FERN_HEIGHT = 300
PNG_SCALE = 3

class FernWriterPng(FernWriter):
	
	def send_move_instr(self, x_dest, y_dest):
		if not self.pen_state:
			self.context.move_to(self.x_state/FERN_WIDTH,self.y_state/FERN_HEIGHT)
			self.context.line_to(x_dest/FERN_WIDTH, y_dest/FERN_HEIGHT)
			self.context.stroke()

		self.x_state = x_dest
		self.y_state = y_dest

		return None
	
	def send_pen_instr(self,new_pen_state):
		self.pen_state = new_pen_state != 0
		return None
   
def main(instruction_file, png_file):

	# setup
	surface = cairo.SVGSurface("tmp.svg",FERN_WIDTH*PNG_SCALE,FERN_HEIGHT*PNG_SCALE)

	# setup context
	context = cairo.Context(surface)
	context.set_source_rgb(1,1,1)
	context.scale(FERN_WIDTH*PNG_SCALE,FERN_HEIGHT*PNG_SCALE)
	context.rectangle(0,0,1,1)
	context.fill()
	context.set_line_width(PEN_WIDTH/FERN_WIDTH)
	context.set_line_cap(cairo.LINE_CAP_ROUND)
	context.set_source_rgb(0,0,0)

	# call writer
	f = FernWriterPng(context)
	f.draw(instruction_file)

	# save
	surface.write_to_png(png_file)

	return None

if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	parser.add_argument('instruction_file',type=str)
	parser.add_argument('png_file',type=str)

	args = parser.parse_args()

	main(args.instruction_file, args.png_file)
