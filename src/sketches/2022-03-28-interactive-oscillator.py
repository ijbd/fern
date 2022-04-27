import numpy as np

import matplotlib.pyplot as plt
import argparse

'''
Want second order underdamped system for radius

theta loops by 2*pi, radius follows ADC voltage reading

setup:
	initial condition 
	boundaries

loop:
- read in set val
- estimate derivatives
- calculate next step
- increment theta


considerations:
- need to limit set point so overshoot doesn't exceed paper lim
- need to borrow a potentiometer from 373 lab

y'' + 2*zeta*w_n*y' + w_n^2*y = u * w_n^2

y = (u*w_n^2 - y'' - 2*zeta*w_n*y')/w_n^2


'''

def get_set_point():

	''' fill this with read adc'''

	return 1

def get_coords(th: float, r: float) -> tuple:
	x = r*np.cos(th)
	y = r*np.sin(th)

	return x, y

def main(omega: float, zeta: float, ts: float) -> None:	
	
	# initial conditions
	r = 0
	dr = 0
	
	# move to starting r
	history =[]

	for theta in np.linspace(0,2*np.pi,1000):
		u = get_set_point()
		
		r = r + .5*ts*dr
		dr2 = omega**2*(u-r) - 2*zeta*omega*dr
		r = r + .5*ts*dr
		dr = dr + ts*dr2

		print(r)
		
		history.append(r)

	fig,ax =plt.subplots()

	ax.plot(history)

	plt.savefig('tmp.png')
	return None

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("omega", type=float, help="natural frequency")
	parser.add_argument("zeta", type=float, help="damping factor")
	parser.add_argument("ts", type=float, help="time step")

	args = parser.parse_args()

	main(args.omega, args.zeta, args.ts)