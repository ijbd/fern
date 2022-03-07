import numpy as np
import random
import argparse

from FernArtist import FernArtist

rng = np.random.default_rng()

def get_square(x0: float, y0: float, x1: float, y1: float, fern: FernArtist):
	
	sides = rng.choice(2,size=2)

	# pen state
	if sides[0]:
		fern.line(x0, y0, x1, y0)

	if sides[1]:
		fern.line(x0, y0, x1, y1)

	return None

	

def build_maze(rows: int, columns: int, fern: FernArtist):

	for r in range(rows):
		for c in range(columns):
			x0 = r / float(rows)
			x1 = (r+1) / float(rows)
			y0 = c / float(columns)
			y1 = (c+1) / float(columns)

			get_square(x0, y0, x1, y1, fern)

	return None

def main(rows: int, columns: int, output_file: str, width: float, height: float, x_offset: float, y_offset: float):
	
	# fern
	fern = FernArtist(width, height, output_file, x_offset, y_offset)

	maze = build_maze(rows, columns, fern)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('rows',type=int)
	parser.add_argument('columns',type=int)
	parser.add_argument('output_file',type=str)
	parser.add_argument('width',type=float)
	parser.add_argument('height',type=float)
	parser.add_argument('x_offset',type=float)
	parser.add_argument('y_offset',type=float)

	args = parser.parse_args()

	main(args.rows, args.columns, args.output_file, args.width, args.height, args.x_offset, args.y_offset)