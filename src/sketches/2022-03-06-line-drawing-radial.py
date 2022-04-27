from cmath import pi
import numpy as np
import argparse
from PIL import Image, ImageOps
from scipy import signal

from FernArtist import FernArtist

FERN_WIDTH = 250
FERN_HEIGHT = 300
PIXEL_SCALE = 3

NUM_BINS = 3 # TODO parametrize
GRAD_THRESHOLD = .15 # TODO parametrize
EDGE_VALUE_THRESHOLD = .9 # TODO parametrize
FILL_VALUE_THRESHOLD = .6 # TODO parametrize

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
 
def load_arr_from_img(img_file: str, scale:float) -> np.ndarray:
	image = Image.open(img_file)
	image.thumbnail((int(FERN_WIDTH*PIXEL_SCALE/scale),int(FERN_HEIGHT*PIXEL_SCALE*scale)))
	image = ImageOps.grayscale(image)

	return np.asarray(image).T / 255.

def digitize_by_value(arr: np.ndarray) -> np.ndarray:
	return np.digitize(arr,np.linspace(0, 1, NUM_BINS))

def detect_edges(arr: np.ndarray) -> np.ndarray:
	
	# edge detection kernel
	kernel = np.array([[-.125, -.125, -.125],
						[-.125, 1, -.125],
						[-.125, -.125, -.125]])

	edges_arr = signal.convolve2d(arr, kernel, boundary='symm', mode='same')

	return edges_arr < -GRAD_THRESHOLD

def dark_filter(edges_arr: np.ndarray, value_arr: np.ndarray) -> np.ndarray:

	dark_fill = value_arr < FILL_VALUE_THRESHOLD
	dark_edges_arr = np.logical_and(value_arr < EDGE_VALUE_THRESHOLD, edges_arr)
	dark_arr = np.logical_or(dark_fill, dark_edges_arr)

	return dark_arr
	
def add_buffer_to_arr(arr: np.ndarray) -> np.ndarray:

	buffer = np.zeros((arr.shape[0] + 2, arr.shape[1] + 2))
	buffer[1:-1, 1:-1] = arr

	return buffer

class Pixel:
	def __init__(self,x,y,val):
		self.x = x
		self.y = y
		self.val = val
		self.drawn = 0

	def __str__(self):
		return f"{self.x, self.y}"

	def __repr__(self):
		return f"{self.x, self.y}"

def build_pixel_arr(arr: np.ndarray) -> list:
	return [[Pixel(x, y, arr[x,y]) for y in range(arr.shape[1])] for x in range(arr.shape[0])]

def populate_pixel_arr(pixel_arr: list, arr: np.ndarray) -> None:

	for row in pixel_arr:
		for pixel in row:
			pixel.val = arr[pixel.x,pixel.y]

	return None

def get_next_clockwise(curr: Pixel, pivot: Pixel, pixel_arr: list) -> Pixel:

	# magnitude of change
	magnitude = 1 if (curr.x < pivot.x or curr.x == pivot.x and curr.y > pivot.y) else -1

	# move left/right
	if curr.y != pivot.y and curr.x - pivot.x != curr.y - pivot.y:
		x = curr.x + magnitude
		y = curr.y

	# move up/down
	else:
		x = curr.x
		y = curr.y + magnitude

	return pixel_arr[x][y]

def has_neighbors(pixel: Pixel, pixel_arr: list) -> bool:
	start = pixel_arr[pixel.x-1][pixel.y]

	if start.val:
		return True

	curr = get_next_clockwise(start, pixel, pixel_arr)

	while curr != start:
		if curr.val:
			return True
		curr = get_next_clockwise(curr, pixel, pixel_arr)

	return False
		
def moore_trace(pixel_arr: list, start: Pixel, prev: Pixel) -> list:
	'''Moore Neighbor tracing (NOT USED)'''

	# set B to be empty
	path = []

	# Insert s in B
	start.drawn = 1

	path.append(start)

	# set p to s
	pivot = start

	# backtrack to pixel from which s was entered
	curr = prev

	# set c to be the next clockwise pixel
	curr = get_next_clockwise(curr, pivot, pixel_arr)

	# while c != s
	while curr != start:

		# if c is black
		if curr.val:
			# insert c into B
			if not curr.drawn:
				path.append(curr)
				curr.drawn = 1

			# set p to c
			pivot = curr

			# backtrack 
			curr = prev
		
		else:
			# advance to next clockwise pixel
			prev = curr

			curr = get_next_clockwise(curr, pivot, pixel_arr)

	return path

def find_p1(pixel: Pixel, pixel_arr: list, direction: int) -> Pixel:
	
	relative_x = -1 if direction in [UP, LEFT] else 1
	relative_y = -1 if direction in [DOWN, LEFT] else 1

	p1 = pixel_arr[pixel.x + relative_x][pixel.y + relative_y]

	return p1
	
def pavlidis_trace(pixel_arr: list, start: Pixel, prev) -> list:
	'''Theo Pavlidis trace'''

	# set B to be empty
	path = []

	# Insert s in B
	path.append(start)
	start.drawn = 1

	# Initialize direction
	direction = UP # 0 - up, 1 - right, 2 - down, 3 - left

	# set p to s
	curr = start

	num_turns = 0

	# keep track of how many times start pixel has been visited
	left_starting = 1
	visited_starting = 0

	# repeat the following
	while True:

		p1 = find_p1(curr, pixel_arr, direction)
		p2 = get_next_clockwise(p1, curr, pixel_arr)
		p3 = get_next_clockwise(p2, curr, pixel_arr)
		p3_right = get_next_clockwise(p3, curr, pixel_arr)

		if p1.val:

			curr = p1
			num_turns = 0
			direction = (direction - 1) % 4

			# move forward and left to p1
			if p2.val and not p2.drawn:
				p2.drawn = 1
				path.append(p2)

			if not p1.drawn:
				p1.drawn = 1
				path.append(p1)

		elif p2.val:

			curr = p2
			num_turns = 0

			# move forward to p2
			if not p2.drawn:
				p2.drawn = 1
				path.append(p2)

		elif p3.val:

			curr = p3
			num_turns = 0

			# move right then left
			if p3_right.val and not p3_right.drawn:
				p3_right.drawn = 1
				path.append(p3_right)

			if not p3.drawn:
				p3.drawn = 1
				path.append(p3)

		elif num_turns == 3:
			return path

		else:
			# rotate 90 degrees clockwise
			direction = (direction + 1) % 4
			num_turns += 1
			left_starting = 0

		if curr == start:
			visited_starting += 1
			left_starting = 1
		if visited_starting > 2:
			return path

def extract_val_arr(pixel_arr: list):
	return np.asarray([[pixel.val for pixel in row] for row in pixel_arr])

def extract_drawn_arr(pixel_arr: list):
	return np.asarray([[pixel.drawn for pixel in row] for row in pixel_arr])

def remove_drawn(pixel_arr:list) -> None:
	for row in pixel_arr:
		for pixel in row:
			if pixel.drawn:
				pixel.val = 0
				
def find_path(pixel_arr: list) -> list:

	path = []

	for row in pixel_arr:
		for pixel in row:
			if pixel.val and has_neighbors(pixel, pixel_arr):

				start = pixel

				path.append(pavlidis_trace(pixel_arr, start, prev))

				remove_drawn(pixel_arr)

			prev = pixel

	return path

def save_arr_to_img(arr: np.ndarray, output_file: str = "tmp.png") -> None:

	img_arr = ((1-arr)*255).astype(np.uint8)
	image = Image.fromarray(img_arr)
	image.save(output_file)
	
	return None

def get_drawing_width_height(arr_width: int, arr_height: int, scale: float) -> tuple:

	if float(arr_width) / FERN_WIDTH > float(arr_height) / FERN_HEIGHT:
		draw_width = FERN_WIDTH * scale
		draw_height = arr_height * FERN_WIDTH / arr_width * scale
	else:
		draw_width = arr_width * FERN_HEIGHT / arr_height * scale
		draw_height = FERN_HEIGHT * scale

	return int(draw_width), int(draw_height)

def draw_to_fern(fern: FernArtist, path, max_x, max_y):
	for segment in path:
		if len(segment) > 1:

			x = round(segment[0].x/float(max_x),4)
			y = round(segment[0].y/float(max_y),4)
			fern.pen(1)
			fern.move(x, y)
			fern.pen(0)

			for point in segment[1:]:
				x_next = round(point.x/float(max_x),4)
				y_next = round(point.y/float(max_y),4)

				if x_next != x or y_next != y:
					fern.move(x_next, y_next)
					x = x_next
					y = y_next

	return

def main(img_file: str, output_file:str, scale: float, x_offset:int, y_offset:int, orientation) -> int:

	# get greay scale array from image
	arr = load_arr_from_img(img_file, scale)

	if orientation == "landscape":
		arr = arr.T

	# discretize borders
	digitized_arr = digitize_by_value(arr)

	# get edges array
	edges_arr = detect_edges(digitized_arr)
	
	edges_arr = dark_filter(edges_arr, arr)

	# add border buffer
	edges_arr = add_buffer_to_arr(edges_arr)

	save_arr_to_img(edges_arr, 'tmp-to-draw.png')

	# build array to track state
	pixel_arr = build_pixel_arr(edges_arr)

	# find path
	path = find_path(pixel_arr)

	save_arr_to_img(extract_drawn_arr(pixel_arr),f"tmp-drawn.png")

	# draw
	draw_width, draw_height = get_drawing_width_height(arr.shape[0], arr.shape[1], scale)
	
	fern = FernArtist(draw_width, draw_height, output_file, x_offset, y_offset)

	draw_to_fern(fern, path, arr.shape[0], arr.shape[1])

	return 0

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("img_file",type=str)
	parser.add_argument("output_file",type=str)
	parser.add_argument("scale",type=float)
	parser.add_argument("x_offset",type=int)
	parser.add_argument("y_offset",type=int)
	parser.add_argument("--orientation",type=str, default="portrait", choices=["landscape","portrait"])
	args = parser.parse_args()

	main(args.img_file, args.output_file, args.scale, args.x_offset, args.y_offset, args.orientation)
