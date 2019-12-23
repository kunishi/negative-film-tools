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

# crop
rgb = rgb[0:(rgb.shape[0] - (rgb.shape[0] % 96)), 0:(rgb.shape[1] - (rgb.shape[1] % 96)), :]

#h, s, v = cv2.split(color.rgb2hsv(rgb))
#gamma = color.hsv2rgb(cv2.merge((h, s, exposure.adjust_gamma(v, gamma=1/2.222, gain=4.5))))
#r, g, b = cv2.split(rgb)
#r_c = exposure.equalize_adapthist(r, clip_limit=0.005)
#g_c = exposure.equalize_adapthist(g, clip_limit=0.005)
#b_c = exposure.equalize_adapthist(b, clip_limit=0.005)
#img_c = cv2.merge((r_c, g_c, b_c))
#contrasted = exposure.adjust_gamma(util.invert(img_c), gamma=args.gamma)
pre = util.invert(rgb)
r, g, b = cv2.split(pre)
kernel_size = (pre.shape[0] // 96, pre.shape[1] // 96)
r_c = exposure.equalize_adapthist(r, clip_limit=0.004, kernel_size=kernel_size)
g_c = exposure.equalize_adapthist(g, clip_limit=0.004, kernel_size=kernel_size)
b_c = exposure.equalize_adapthist(b, clip_limit=0.004, kernel_size=kernel_size)
contrasted = exposure.adjust_gamma(cv2.merge((r_c, g_c, b_c)), gamma=1/1.1)
#contrasted = exposure.adjust_gamma(exposure.equalize_adapthist(pre, clip_limit=0.004, kernel_size=(pre.shape[0] // 96, pre.shape[1] // 96)), gamma=1/1.1)
h, s, v = cv2.split(color.rgb2hsv(contrasted))
merged = color.hsv2rgb(cv2.merge((h, s + 10.0 / 200.0, v + 12.0 / 200.0)))

result = merged
if args.out:
    io.imsave(os.path.abspath(args.out), result)
else:
    io.imshow((result / 255).astype('uint8'))
    io.show()
