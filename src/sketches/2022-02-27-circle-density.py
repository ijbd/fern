import os
import numpy as np
import random

from FernArtist import FernArtist

local_dir = os.path.dirname(__file__)

def get_filename():
	return os.path.join(local_dir,'..','..','prints',f"2022-02-27-tmp.f")
	
def draw_radial_scribbles(fern: FernArtist):

	xc = .5
	yc = .5
	r = .3

	# move to start
	fern.move(xc+r, yc)
	fern.pen(0)

	for theta in np.linspace(0,8*np.pi,100):

		x = xc + r*np.cos(theta)
		y = yc + r*np.sin(theta)

		thetao = theta - .1 + .2*random.random()
		ro = r + .1+.1*random.random()
		xo = xc + ro*np.cos(thetao)
		yo = yc + ro*np.sin(thetao)


		# move
		fern.move(x,y)
		fern.move(xo,yo)

	pass

def main():
	fern = FernArtist(50,50,get_filename(),10,100)
	
	draw_radial_scribbles(fern)

if __name__ == '__main__':
	main()