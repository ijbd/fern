import cairo
import random
import math
import sys, os
import numpy as np
import datetime

from PIL import Image, ImageOps

localDir = os.path.dirname(__file__)

PENWIDTH = .5

class Artist:
	def __init__(self,width,height,filename,offsetX=0,offsetY=0,scale=1):
		self.width = width*scale
		self.height = height*scale
		self.filename = filename
		
		# make surface
		self.surface = cairo.SVGSurface(os.path.join(localDir,'tmp.svg'),self.width,self.height)
			
		# setup
		self.c = cairo.Context(self.surface)
		self.c.scale(self.width,self.height)

		# setup
		self.c.set_source_rgb(1,1,1)
		self.c.rectangle(0,0,1,1)
		self.c.fill()
		
		# line setup
		self.c.set_line_width(PENWIDTH/width)
		self.c.set_line_cap(cairo.LINE_CAP_ROUND)
		self.c.set_source_rgb(0,0,0)

	def line(self,x1,y1,x2,y2):
		self.c.move_to(x1,y1)
		self.c.line_to(x2,y2)
		self.c.stroke()

	def rect(self,x1,y1,x2,y2):
		self.line(x1,y1,x1,y2)
		self.line(x1,y2,x2,y2)
		self.line(x2,y2,x2,y1)
		self.line(x2,y1,x1,y1)
	
	def circumRect(self,xc,yc,rad):
		self.rect(xc-rad,yc-rad,xc+rad,yc+rad)

	def circle(self,xc,yc,r):
		self.c.arc(xc,yc,r,0,2*math.pi)
		self.c.stroke()

	def save(self,outputFile=None):
		self.surface.write_to_png(outputFile if outputFile is not None else self.filename)
		