#!/usr/bin/python3
import os, sys
import argparse
import rawpy
import cv2
import numpy as np
from skimage import color, exposure, io, util

parser = argparse.ArgumentParser()
parser.add_argument("src", help="source RAW file")
parser.add_argument("--bw", help="run in bw mode", action="store_true")
parser.add_argument("--gamma", help="specify gamma value", type=float, default=1.8)
parser.add_argument("--out", help="specify the destination TIFF file")
args = parser.parse_args()

raw = rawpy.imread(args.src)
rgb = raw.postprocess(gamma=(1, 1), no_auto_bright=False, use_camera_wb=False, use_auto_wb=True, output_bps=16)

# read image from array
#image = Image.fromarray(rgb)
#image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
image = rgb.copy()

# invert image
#imageBox = image.getbbox()
#cropped = image.crop(imageBox)
#inverted = PIL.ImageOps.invert(cropped)
#inverted = cv2.bitwise_not(image)
#inverted = rgb
inverted = util.invert(image)

# gamma correction and auto contrast
if args.bw:
    if image.shape[2] == 3:
        bw = color.rgb2grey(inverted)
    else:
        bw = inverted
    rgb_gamma = exposure.adjust_gamma(bw, gamma=args.gamma)
    contrasted = exposure.rescale_intensity(rgb_gamma)
else:
    rgb_gamma = exposure.adjust_gamma(inverted, gamma=args.gamma)
    r, g, b = cv2.split(rgb_gamma)
    r_c = exposure.rescale_intensity(r)
    g_c = exposure.rescale_intensity(g)
    b_c = exposure.rescale_intensity(b)
    contrasted = cv2.merge((r_c, g_c, b_c))

result = contrasted
if args.out:
    io.imsave(os.path.abspath(args.out), result)
else:
    io.imshow((result / 255).astype('uint8'))
    io.show()
