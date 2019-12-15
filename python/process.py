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
parser.add_argument("--out", help="specify the destination TIFF file")
args = parser.parse_args()

raw = rawpy.imread(args.src)
rgb = raw.postprocess(no_auto_bright=False, use_camera_wb=False, use_auto_wb=True, output_bps=16)

# gamma correction and auto contrast
if rgb.shape[2] == 1:
    img_c = exposure.rescale_intensity(gamma)
else:   # color, rgb.shape[2] == 3
    r, g, b = cv2.split(rgb)
    r_c = exposure.rescale_intensity(r)
    g_c = exposure.rescale_intensity(g)
    b_c = exposure.rescale_intensity(b)
    if args.bw:
        img_c = color.rgb2grey(cv2.merge((r_c, g_c, b_c)))
    else:
        img_c = cv2.merge((r_c, g_c, b_c))
contrasted = exposure.adjust_gamma(util.invert(img_c), gamma=args.gamma)

result = contrasted
if args.out:
    io.imsave(os.path.abspath(args.out), result)
else:
    io.imshow((result / 255).astype('uint8'))
    io.show()
