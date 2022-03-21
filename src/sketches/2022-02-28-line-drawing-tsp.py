from PIL import Image, ImageOps
import numpy as np 
import os
import argparse
from scipy import signal
from FernArtist import FernArtist

NUM_BINS = 5
PIXEL_SCALE = 4.0
FERN_WIDTH = 250
FERN_HEIGHT = 300

local_dir = os.path.dirname(__file__)

def get_filename():
	return os.path.join(local_dir,'..','..','prints',f"2022-02-28-tmp.f")

def load_image_arr(filename):
	image = Image.open(filename)
	image.thumbnail((FERN_WIDTH*PIXEL_SCALE,FERN_HEIGHT*PIXEL_SCALE))
	image = ImageOps.grayscale(image)

	arr = np.asarray(image)/255.

	return arr.T

def get_edges(arr):

	edges = np.digitize(arr, np.linspace(0,1,NUM_BINS))

	kernel = np.array([[-.125, -.125, -.125],
						[-.125, 1, -.125],
						[-.125, -.125, -.125]])

	edges = signal.convolve2d(edges, kernel, boundary='symm', mode='same')
	return (edges < -.1).astype(np.uint8)

class Pixel:
	def __init__(self,x,y,val):
		self.x = x
		self.y = y
		self.val = val
		self.visited = 0

	def __str__(self):
		return f"({self.x, self.y})"

	def __repr__(self):
		return f"{self.x, self.y}"

def visit_pixel(pixel: Pixel, queue):
	if pixel.visited == 0:
		pixel.visited = 1
		
		if pixel.val != 0:
			queue.append(pixel)

	return None

def get_groups(edges):

	# initialize map
	pixels = [[Pixel(x,y,edges[x,y]) for y in range(edges.shape[1])] for x in range(edges.shape[0])]
	groups = [[]]
	queue = []

	for x in range(len(pixels)):
		for y in range(len(pixels[0])):

			if pixels[x][y].visited == 0:
				queue.append(pixels[x][y])

				if len(groups[-1]) > 0:
					groups.append([])
				
			while len(queue) > 0:

				pixel = queue.pop()

				if pixel.val != 0:
					groups[-1].append(pixel)
					
				is_left = pixel.x == 0
				is_right = pixel.x == (len(pixels) - 1)
				is_top = pixel.y == 0
				is_bottom = pixel.y == (len(pixels[0]) - 1)

				# ul
				if not is_left and not is_top:
					visit_pixel(pixels[pixel.x-1][pixel.y-1],queue)
				
				# l
				if not is_left:
					visit_pixel(pixels[pixel.x-1][pixel.y],queue)

				# bl
				if not is_left and not is_bottom:
					visit_pixel(pixels[pixel.x-1][pixel.y+1],queue)

				# b
				if not is_bottom:
					visit_pixel(pixels[pixel.x][pixel.y+1],queue)

				# br
				if not is_right and not is_bottom:
					visit_pixel(pixels[pixel.x+1][pixel.y+1],queue)

				# r
				if not is_right:
					visit_pixel(pixels[pixel.x+1][pixel.y],queue)

				# ur
				if not is_right and not is_top:
					visit_pixel(pixels[pixel.x+1][pixel.y-1],queue)
				
				# u
				if not is_top:
					visit_pixel(pixels[pixel.x][pixel.y-1],queue)

	if len(groups[-1]) == 0:
		groups.pop()

	return groups

def get_distance(a:Pixel, b:Pixel):
	return (a.x-b.x)**2 + (a.y-b.y)**2

def tsp(group):
	'''greedy tsp'''
	remaining = group.copy()
	path = []

	# start at first spot
	path.append(remaining.pop())

	while len(remaining) > 0:
		min_idx = 0
		min_dist = get_distance(path[-1],remaining[0])

		for i in range(1,len(remaining)):
			dist = get_distance(path[-1],remaining[i])
			if dist < min_dist:
				min_idx = i
				min_dist = dist

		path.append(remaining.pop(min_idx))

	return path

def get_path(groups):

	path = []

	for group in groups:
		path += tsp(group)

	return path

def get_segments(path):
	
	segments = [[]]
	segments[-1].append(path[0])

	for pixel in path[1:]:
		if abs(segments[-1][-1].x - pixel.x) > 1 or abs(segments[-1][-1].x - pixel.x) > 1:
			# start new segment
			segments.append([])

		# add pixel
		segments[-1].append(pixel)

	if len(segments[-1]) == 0:
		segments.pop()
		
	return segments

def get_shortened_segments(segments):

	new_segments = []

	for seg in segments:
		new_seg = []
		new_seg.append(seg[0])

		for i in range(1,len(seg)-1):
			cond1 = seg[i].x - seg[i-1].x != seg[i+1].x - seg[i].x
			cond2 = seg[i].y - seg[i-1].y != seg[i+1].y - seg[i].y
			if cond1 or cond2:
				new_seg.append(seg[i])
		new_seg.append(seg[-1])
		
		if len(new_seg) > 2:
			new_segments.append(new_seg)
	
	return new_segments

def save_image(edges):
	image = Image.fromarray((1-edges)*255)
	image.save('tmp.png')

def write_segments_to_fern(fern: FernArtist,segments, x_max: float, y_max: float):
	for seg in segments:
		if len(seg) > 3:
			fern.pen(1)
			fern.move(seg[0].x / x_max, seg[0].y / y_max)
			fern.pen(0)

			for pixel in seg[1:]:
				fern.move(pixel.x / x_max, pixel.y / y_max)

		


def main(img_filename, scale, x_offset, y_offset):
	arr = load_image_arr(img_filename)
	edges = get_edges(arr)

	save_image(edges)

	groups = get_groups(edges)
	path = get_path(groups)
	segments = get_segments(path)
	segments = get_shortened_segments(segments)

	fern = FernArtist(arr.shape[0]*scale/PIXEL_SCALE, arr.shape[1]*scale/PIXEL_SCALE, get_filename(), x_offset, y_offset)

	write_segments_to_fern(fern, segments, arr.shape[0], arr.shape[1])


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('image_filename',type=str)
	parser.add_argument('scale',type=float)
	parser.add_argument('x_offset',type=float)
	parser.add_argument('y_offset',type=float)

	args = parser.parse_args()

	main(args.image_filename, args.scale, args.x_offset, args.y_offset)

