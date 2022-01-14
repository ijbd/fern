import cairo
import random
import math
import sys, os
import numpy as np
import datetime

from PIL import Image, ImageOps

localDir = os.path.dirname(__file__)

class FernArtist:
	def __init__(self,width,height,filename,offsetX=0,offsetY=0,scale=1):
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.width = width
		self.height = height
					
		# setup
		self.c = open(filename,'w')

	def line(self,x1,y1,x2,y2):
		instruction = ' '.join(['L',
						str(round(x1*self.width+self.offsetX,1)),
						str(round(y1*self.height+self.offsetY,1)),
						str(round(x2*self.width+self.offsetX,1)),
						str(round(y2*self.height+self.offsetY,1))])
		self.c.write(instruction+'\n')

	def rect(self,x1,y1,x2,y2):
		self.line(x1,y1,x1,y2)
		self.line(x1,y2,x2,y2)
		self.line(x2,y2,x2,y1)
		self.line(x2,y1,x1,y1)
	
	def circumRect(self,xc,yc,rad):
		self.rect(xc-rad,yc-rad,xc+rad,yc+rad)

	def circle(self,xc,yc,r):
		instruction = ' '.join(['C',
						str(round(xc*self.width+self.offsetX,1)),
						str(round(yc*self.height+self.offsetY,1)),
						str(round(r,1))])
		self.c.write(instruction+'\n')
	
	def arc(self,xc,yc,r,ts,te):
		pass

	def save(self,outputFile=None):
		pass