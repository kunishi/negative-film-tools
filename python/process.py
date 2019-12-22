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
parser.add_argument("--globalrescale", help="rescaling globally", action="store_true")
parser.add_argument("--noadapt", help="run without adaptive histogram equalization", action="store_true")
parser.add_argument("--positive", help="input the positive image", action="store_true")
parser.add_argument("--rgb", help="input RGB image", action="store_true")
parser.add_argument("--out", help="specify the destination TIFF file")
args = parser.parse_args()

def adaptive_hist(img):
    return exposure.equalize_adapthist(img, clip_limit=0.004, kernel_size=96)

def rescale_intensity(img):
    v_min, v_max = np.percentile(img, (0.2, 99.8))
    print(v_min, v_max)
    return exposure.rescale_intensity(img, in_range=(v_min, v_max))

if args.rgb:
    image = io.imread(args.src, as_gray=args.bw)
    if args.positive:
        rgb = image
    else:
        rgb = exposure.adjust_gamma(util.invert(image), gamma=2.222)
else:
    raw = rawpy.imread(args.src)
    rgb = util.invert(raw.postprocess(gamma=(2.222, 4.5), no_auto_bright=False, auto_bright_thr=0.01, use_camera_wb=False, use_auto_wb=True, output_bps=16))

# gamma correction and auto contrast
if len(rgb.shape) == 2 or rgb.shape[2] == 1:
    args.bw = True
    img_src = rgb
else:   # color, rgb.shape[2] == 3
    if args.bw:
        img_src = color.rgb2gray(rgb)
    else:
        img_src = rgb

if args.noadapt:
    contrasted = img_src / 65536
elif args.bw:
    contrasted = rescale_intensity(adaptive_hist(img_src))
elif args.globalrescale:
    r, g, b = cv2.split(img_src)
    r_c = adaptive_hist(r)
    g_c = adaptive_hist(g)
    b_c = adaptive_hist(b)
    contrasted = rescale_intensity(cv2.merge((r_c, g_c, b_c))
else:
    r, g, b = cv2.split(img_src)
    r_c = rescale_intensity(adaptive_hist(r))
    g_c = rescale_intensity(adaptive_hist(g))
    b_c = rescale_intensity(adaptive_hist(b))
    contrasted = cv2.merge((r_c, g_c, b_c))

result = exposure.adjust_gamma(contrasted, gamma=args.gamma)

if args.out:
    io.imsave(os.path.abspath(args.out), result)
else:
    io.imshow(result)
    io.show()
