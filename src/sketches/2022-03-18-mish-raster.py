import numpy as np
from PIL import Image, ImageOps
import argparse

from FernArtist import FernArtist

FERN_WIDTH = 200
FERN_HEIGHT = 300
FERN_PIXEL_SCALE = 2

def load_image(image_file: str) -> Image:

	return Image.open(image_file)

def convert_rgb_to_gs(image: Image) -> Image:
	
	return ImageOps.grayscale(image)

def convert_image_to_arr(image: Image) -> np.ndarray:
	
	return np.asarray(image).T

def normalize_value_arr(value_arr: np.ndarray) -> np.ndarray:
	
	return value_arr / 255.

def convert_value_to_bit_arr(value_arr: np.ndarray) -> np.ndarray:

	return value_arr < np.max(value_arr)

def travel_bit_arr(bit_arr: np.ndarray) -> list:

	n_rows = bit_arr.shape[0]
	n_cols = bit_arr.shape[1]

	path = list()
	diag_path = list()

	for line in range(1, (n_rows + n_cols)):
		
		start_col = max(0, line - n_rows)

		count = min(line, (n_cols - start_col), n_rows)

		for j in range(0, count):
			x = min(n_rows, line) - j - 1
			y = start_col + j

			if bit_arr[x][y]:
				diag_path.append((x,y))

		if len(diag_path) > 0:
			if line % 2:
				path += diag_path
			else:
				diag_path.reverse()
				path += diag_path

			diag_path = list()

	return path

def convert_to_segments (path: list) -> list:

	segments = list()
	seg = list()
	seg.append(path[0])

	for pixel in path[1:]:
		if abs(seg[-1][0] - pixel[0]) > 1 or abs(seg[-1][1] - pixel[1]) > 1:
			# start new segment
			segments.append(seg)
			seg = list()

		# add pixel
		seg.append(pixel)
	
	if len(seg) > 0:
		segments.append(seg)
		
	return segments

def reduce_segments(segments: list) -> list:

	new_segments = list()

	for seg in segments:
		new_seg = list()
		new_seg.append(seg[0])

		for i in range(1,len(seg)-1):
			cond1 = seg[i][0] - seg[i-1][0] != seg[i+1][0] - seg[i][0]
			cond2 = seg[i][1] - seg[i-1][1] != seg[i+1][1] - seg[i][1]
			if cond1 or cond2:
				new_seg.append(seg[i])
		new_seg.append(seg[-1])
		
		if len(new_seg) > 1:
			new_segments.append(new_seg)
	
	return new_segments

def convert_bit_arr_to_value(bit_arr: np.ndarray) -> np.ndarray:

	return (bit_arr * 255).astype(np.uint8)

def save_bit_arr_to_image(bit_arr: np.ndarray, image_file: str="tmp.png") -> None:

	inverted_bit_arr = 1 - bit_arr
	gs_arr = convert_bit_arr_to_value(inverted_bit_arr)

	image = Image.fromarray(gs_arr.T)
	image.save(image_file)
	
	return None
	
def get_drawing_width_height(arr_width: int, arr_height: int, scale: float) -> tuple:

	if float(arr_width) / FERN_WIDTH > float(arr_height) / FERN_HEIGHT:
		draw_width = FERN_WIDTH * scale
		draw_height = arr_height * FERN_WIDTH / arr_width * scale
	else:
		draw_width = arr_width * FERN_HEIGHT / arr_height * scale
		draw_height = FERN_HEIGHT * scale

	return int(draw_width), int(draw_height)


def draw_segments_to_fern(fern: FernArtist, segments: list, arr_width: float, arr_height: float) -> None:
	
	all_x = []
	all_y = []

	for seg in segments:
		fern.pen(1)
		x = seg[0][0]/arr_width
		y = seg[0][1]/arr_height
		fern.move(x, y)
		fern.pen(0)

		all_x.append(x)
		all_y.append(y)

		for pixel in seg[1:]:
			x = pixel[0]/arr_width
			y = pixel[1]/arr_height
			fern.move(x, y)

			all_x.append(x)
			all_y.append(y)

	print(np.min(all_x)*fern.width+fern.offsetX, np.max(all_x)*fern.width+fern.offsetX)
	print(np.min(all_y)*fern.height+fern.offsetY, np.max(all_y)*fern.height+fern.offsetY)
	return None

def main(image_file: str, output_file: str, scale: float):

	rgb_image = load_image(image_file)
	gs_image = convert_rgb_to_gs(rgb_image)
	gs_arr = convert_image_to_arr(gs_image)
	norm_gs_arr = normalize_value_arr(gs_arr)
	bit_arr = convert_value_to_bit_arr(norm_gs_arr)

	save_bit_arr_to_image(bit_arr)

	path = travel_bit_arr(bit_arr)
	segments = convert_to_segments(path)
	segments = reduce_segments(segments)
	
	draw_width, draw_height = get_drawing_width_height(bit_arr.shape[0], bit_arr.shape[1], scale)
	
	fern = FernArtist(draw_width, draw_height, output_file, 0, 15)

	draw_segments_to_fern(fern, segments, bit_arr.shape[0], bit_arr.shape[1])

	return 0

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("image_file",type=str)
	parser.add_argument("output_file",type=str)
	parser.add_argument("scale",type=float)

	args = parser.parse_args()

	main(args.image_file, args.output_file, args.scale)
