import numpy as np
import argparse

from FernArtist import FernArtist

rng = np.random.default_rng()

def in_bounds(x,y):
	return abs(x) < 1 and abs(y) < 1

def generate_scribble(fern: FernArtist, x_center, y_center, size):

	coeff = [2+4*rand_float for rand_float in rng.random(4)]

	t = np.linspace(0, np.pi, 100)

	x_arr = x_center + size*(np.sin(coeff[0]*t)/2.0 + np.cos(coeff[0]*t)/2.0)
	y_arr = y_center + size*(np.sin(coeff[1]*t)/2.0 + np.cos(coeff[1]*t)/2.0)

	if not in_bounds(x_arr[0], y_arr[0]):
		return None

	# move to starting position
	fern.pen(1)
	fern.move(x_arr[0], y_arr[0])
	fern.pen(0)

	# iterate
	for (x, y) in zip(x_arr, y_arr):
		if not in_bounds(x, y):
			return None
		
		fern.move(x, y)
		
	return None

def main(fern_filename, width, height, offset_x, offset_y):
	
	# fern
	fern = FernArtist(width, height, fern_filename, offset_x, offset_y)

	# scribbles 
	for n in np.linspace(0, 2*np.pi, 20):

		x_center = .5 + .4*np.cos(n)*np.exp(-.1*n)
		y_center = .5 + .4*np.sin(n)*np.exp(-.1*n)
		size = .05
		generate_scribble(fern, x_center, y_center, size)


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('fern_filename',type=str)
	parser.add_argument('width',type=float)
	parser.add_argument('height',type=float)
	parser.add_argument('offset_x',type=float)
	parser.add_argument('offset_y',type=float)
	
	args = parser.parse_args()

	main(args.fern_filename, args.width, args.height, args.offset_x, args.offset_y)

