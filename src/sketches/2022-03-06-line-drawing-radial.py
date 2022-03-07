import numpy as np
import argparse
from PIL import Image, ImageOps

from FernArtist import FernArtist

FERN_WIDTH = 250
FERN_HEIGHT = 300
PIXEL_SCALE = 4


def load_arr_from_img(img_file):
	image = Image.open(img_file)
	image.thumbnail((FERN_WIDTH*PIXEL_SCALE,FERN_HEIGHT*PIXEL_SCALE))
	image = ImageOps.grayscale(image)

	return np.asarray(image).T / 255.

def save_arr_to_img(arr, output_file='tmp.png'):
	img_arr = (arr*255).astype(np.uint8)
	image = Image.fromarray((img_arr)
	image.save(output_file)

def main(img_file):

	arr = load_arr_from_img(img_file)


	pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("img_file",type=str)
	args = parser.parse_args()

	main(args.img_file)