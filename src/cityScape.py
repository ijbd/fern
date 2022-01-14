import math
import random
import os
import sys
import datetime

from Artist import Artist
from FernArtist import FernArtist

WIDTH = 200
HEIGHT = 200
PENWIDTH = .5

LOCALDIR = os.path.dirname(__file__)

class Building:
	def __init__(self,x1,y1,x2,y2):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2

class CityScape:
	
	def __init__(self,artist):
		self.artist = artist
		self.buildings = []

	def drawBuilding(self,x,w,h):
		
		# get corneras
		x1 = abs(x) - abs(w)/2.
		x2 = abs(x) + abs(w)/2.
		y1 = .5 - abs(h)/2.
		y2 = .5 + abs(h)/2.

		b = Building(x1,y1,x2,y2)
		
		top = [(x1,x2)] # line segments
		left = [.5,y1]
		right = [.5,y1]

		for other in self.buildings:
			# get left
			if x1 > other.x1 and x1 < other.x2:
				if y1 > other.y1:
					left.clear()
				elif len(left) > 0:
					left[0] = min(left[0],other.y1)

			# get right
			if x2 > other.x1 and x2 < other.x2:
				if y1 > other.y1:
					right.clear()
				elif len(right) > 0:
					right[0] = min(right[0],other.y1)

			# get top
			if y1 > other.y1:
				
				newTop = []

				while len(top) > 0:

					segment = top.pop()
				
					# left segment
					if other.x1 > segment[0]:
						newTop.append((segment[0],min(segment[1],other.x1)))
					# right segment
					if other.x2 < segment[1]:
						newTop.append((max(segment[0],other.x2),segment[1]))
				
				top = newTop

		# draw left
		if len(left) > 0:
			self.artist.line(x1,left[0],x1,left[1])
			self.artist.line(x1,1-left[0],x1,1-left[1])
		
		# draw right
		if len(right) > 0:
			self.artist.line(x2,right[0],x2,right[1])
			self.artist.line(x2,1-right[0],x2,1-right[1])
			
		# draw top
		for segment in top:
			self.artist.line(segment[0],y1,segment[1],y1)
			self.artist.line(segment[0],y2,segment[1],y2)
				
		self.buildings.append(b)

def main(artist):
	

	city = CityScape(artist)

	# draw
	n = 100

	for i in range(n):
		x = .1 + .8*random.random()
		h = 2*math.sin(i*math.pi/n)*(x-.5)*(x)*(x-1)*random.random()
		w = .001 + .05*random.random()
		city.drawBuilding(x,w,h)

	
	for i in range(n):
		x = .3 + .6*random.random()
		h = math.sin(i*x*math.pi/n)*(x-1)*random.random()
		w = .005 + .05*random.random()
		city.drawBuilding(x,w,h)
	
	artist.line(0,.5,1,.5)

	# save
	artist.save()

if __name__ == '__main__':

	if sys.argv[1] == 'fern':
		outputFile = outputFile = os.path.join(LOCALDIR,
			'..',
			'prints',
			datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.f')
		artist = FernArtist(WIDTH,HEIGHT,outputFile,offsetX=3,offsetY=3)

	elif sys.argv[1] == 'png':
		outputFile = outputFile = os.path.join(LOCALDIR,
			'..',
			'images',
			datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.png')

		artist = Artist(WIDTH,HEIGHT,outputFile,scale=10)
	else:
		sys.exit(1)
	main(artist)