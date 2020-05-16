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
parser.add_argument("--bwitur", help="run in bw mode based on ITU-R BT.601", action="store_true")
parser.add_argument("--bwhsv", help="run in bw mode based on HSV", action="store_true")
parser.add_argument("--gamma", help="specify gamma value", type=float, default=1.0)
parser.add_argument("--rawgamma", help="specify gamma value in RAW processing", type=float, default=2.25)
parser.add_argument("--globalrescale", help="rescaling globally", action="store_true")
parser.add_argument("--noadapt", help="run without adaptive histogram equalization", action="store_true")
parser.add_argument("--linearraw", help="process RAW image without gamma correction", action="store_true")
parser.add_argument("--useautobrightness", help="disable auto brightness mode in libraw", action="store_true")
parser.add_argument("--useautowb", help="enable auto white balance mode in libraw", action="store_true")
parser.add_argument("--greengamma", help="gamma fix only to green channel", action="store_true")
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

def rgb2gray(img, gamma=1.8):
    #linear = exposure.adjust_gamma(img, 1/gamma)
    #bnw = color.rgb2gray(linear)
    #return exposure.adjust_gamma(bnw, gamma)
    return color.rgb2gray(img)

def rgb2gray_itur(img, gamma=1.5):
    coeffs = np.array([0.299, 0.587, 0.114], dtype=img.dtype)
    #return exposure.adjust_gamma(img @ coeffs, gamma)
    return img @ coeffs

def rgb2gray_hsv(img, gamma=1.0):
    h, s, v = cv2.split(color.rgb2hsv(img))
    #return exposure.adjust_gamma(v, gamma)
    return v

if args.rgb:
    image = io.imread(args.src, as_gray=args.bw)
    if args.positive:
        rgb = image
    else:
        rgb = exposure.adjust_gamma(util.invert(image), gamma=2.222)
else:
    raw = rawpy.imread(args.src)
    if args.linearraw:
        rgb = raw.postprocess(gamma=(1.0, 1.0),
                                demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
                                dcb_enhance=True,
                                no_auto_bright=not args.useautobrightness,
                                auto_bright_thr=0.01,
                                use_camera_wb=False,
                                use_auto_wb=args.useautowb,
                                output_bps=16)
    else:
        rgb = raw.postprocess(gamma=(args.rawgamma, 4.5),
                                demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
                                dcb_enhance=True,
                                no_auto_bright=not args.useautobrightness,
                                auto_bright_thr=0.01,
                                use_camera_wb=False,
                                use_auto_wb=args.useautowb,
                                output_bps=16)

img_src = rgb

if args.noadapt:
    contrasted = img_src / 65536
elif args.globalrescale:
    r, g, b = cv2.split(img_src)
    r_c = adaptive_hist(r)
    g_c = adaptive_hist(g)
    b_c = adaptive_hist(b)
    contrasted = util.invert(rescale_intensity(cv2.merge((r_c, g_c, b_c))))
elif args.bw or args.bwitur or args.bwhsv:
    if args.bw:         # for bnw films
        gray = rgb2gray(img_src)
    elif args.bwitur:   # for color films to bnw
        gray = rgb2gray_itur(img_src)
    elif args.bwhsv:
        gray = rgb2gray_hsv(img_src)
    contrasted = util.invert(rescale_intensity(adaptive_hist(gray)))
else:
    r, g, b = cv2.split(img_src)
    r_c = rescale_intensity(adaptive_hist(r))
    if args.greengamma:
        g_c = exposure.adjust_gamma(rescale_intensity(adaptive_hist(g)), gamma=1.08)
    else:
        g_c = rescale_intensity(adaptive_hist(g))
    b_c = rescale_intensity(adaptive_hist(b))
    contrasted = util.invert(cv2.merge((r_c, g_c, b_c)))

result = exposure.adjust_gamma(contrasted, gamma=args.gamma)

if args.out:
    io.imsave(os.path.abspath(args.out), result)
else:
    io.imshow(result)
    io.show()
