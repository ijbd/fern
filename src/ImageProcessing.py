import numpy as np
from PIL import Image
import argparse

class FernImageProcessor:
	XMAX = 200
	YMAX = 300

	def __init__(self, penWidth):
		self.penWidth = penWidth

	def processImage(self,originFile,xc,yc,size,orientation):
		# open image 
		image = Image.open(originFile)

		# resize image according to 

		# rotate if necessary

		# place image on larger array according to size
			# find largest size to fit (gvien XMAX and YMAX)
		pass


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Image processing script for Fern images. Resize, scale, and move images into correct positions')
	parser.add_argument('origin_file',type=str,help='Filepath to the source image.')
	parser.add_argument('--x-center',type=int,default=FernImageProcessor.XMAX/2,help='X coordinate to move center of image (mm)')
	parser.add_argument('--y-center',type=int,default=FernImageProcessor.YMAX/2,help='Y coordinate to move center of image (mm)')
	parser.add_argument('--size',type=int,default=FernImageProcessor.YMAX,help='Side length of square in which image is attempted to scale to (mm)')
	parser.add_argument('--orientation',type=str,options=['portrait','landscape'])
	parser.add_argument('--pen-width',type=float,default='.5',help='Pen line thickness (mm)')

	args = parser.parse_args()
	
	i = FernImageProcessor(args.pen_width)
	i.processImage(args.origin_file,args.x_center,args.y_center,args.size,args.orientation)




