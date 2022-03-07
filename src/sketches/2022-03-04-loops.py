import numpy as np
import argparse

from FernArtist import FernArtist

rng = np.random.default_rng()

def build_loops(fern: FernArtist) -> None:

	n = 20000
	t = np.linspace(0, 2*np.pi, n)
	v = 1/(2*np.pi)

	f1 = 150
	f2 = 150

	a1 = .2+.1*np.sin(5*t)
	a2 = .1

	e1 = np.exp(-(t-np.pi)**2/2)
	e2 = np.exp(-(t-np.pi)**2/2)

	p1 = 0#np.cos(t)
	p2 = .2#np.cos(t)
	
	x_arr = .5 + a1*np.cos(f1*t + p1)*e1
	y_arr = v*t + a2*np.sin(f2*t + p2)*e2

	fern.move(x_arr[0], y_arr[0])
	fern.pen(0)

	for x, y in zip(x_arr, y_arr):
		fern.move(x, y)

	return None

def build_loops_shaky(fern: FernArtist) -> None:

	n = 20000
	t = np.linspace(0, 2*np.pi, n)

	vx = 0
	vy = 1/(2*np.pi)

	fx = 200
	fy = 200

	ax = .2+.1*np.sin(8*t)
	ay = .1

	e = np.exp(-(t-np.pi)**2/2)

	px = np.cos(t)
	py = 0
	
	x_arr = .5 + vx*t + ax*np.cos(fx*t + px)*e
	y_arr = vy*t + ay*np.sin(fy*t + py)*e

	fern.move(x_arr[0], y_arr[0])
	fern.pen(0)

	for x, y in zip(x_arr, y_arr):
		fern.move(x, y)

	return None

def main(fern: FernArtist) -> int:
	
	build_loops_shaky(fern)

	return 0

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('output_file',type=str)
	parser.add_argument('width',type=float)
	parser.add_argument('height',type=float)
	parser.add_argument('x_offset',type=float)
	parser.add_argument('y_offset',type=float)

	args = parser.parse_args()

	fern = FernArtist(args.width, args.height, args.output_file, args.x_offset, args.y_offset)

	main(fern)