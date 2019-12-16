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
parser.add_argument("--gamma", help="specify gamma value", type=float, default=1.0)
parser.add_argument("--hsv", help="CLAHE on HSV mode", action="store_true")
parser.add_argument("--out", help="specify the destination TIFF file")
args = parser.parse_args()

raw = rawpy.imread(args.src)
rgb = raw.postprocess(no_auto_bright=False, use_camera_wb=False, use_auto_wb=True, output_bps=16)

# gamma correction and auto contrast
if rgb.shape[2] == 1:
    args.bw == True
    img_src = rgb
else:   # color, rgb.shape[2] == 3
    if args.bw:
        img_src = color.rgb2gray(rgb)
    else:
        img_src = rgb

if args.bw:
    contrasted = exposure.equalize_adapthist(img_src, clip_limit = 0.004, kernel_size = 96)
elif args.hsv:
    contrasted = exposure.equalize_adapthist(img_src, clip_limit = 0.004, kernel_size = 96)
else:
    r, g, b = cv2.split(img_src)
    r_c = exposure.equalize_adapthist(r, clip_limit = 0.004, kernel_size = 96)
    g_c = exposure.equalize_adapthist(g, clip_limit = 0.004, kernel_size = 96)
    b_c = exposure.equalize_adapthist(b, clip_limit = 0.004, kernel_size = 96)
    contrasted = cv2.merge((r_c, g_c, b_c))

result = exposure.adjust_gamma(util.invert(contrasted), gamma=args.gamma)

if args.out:
    io.imsave(os.path.abspath(args.out), result)
else:
    io.imshow((result / 255).astype('uint8'))
    io.show()
