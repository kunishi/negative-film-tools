#!/usr/bin/python3
import os, sys
import argparse
import rawpy
import cv2
import numpy as np
from skimage import color, exposure, io, util

def parse_args():
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
    parser.add_argument("--positive", help="input the positive image", action="store_true")
    parser.add_argument("--withoutrescale", help="do not process rescaling", action="store_true")
    parser.add_argument("--rgb", help="input RGB image", action="store_true")
    parser.add_argument("--out", help="specify the destination TIFF file")
    return parser.parse_args()

def adaptive_hist(img):
    return exposure.equalize_adapthist(img, clip_limit=0.004, kernel_size=96)

def rescale_intensity(img, withoutrescale=False):
    v_min, v_max = np.percentile(1.0 * img, (0.03, 99.97))
    print(v_min, v_max)
    if not withoutrescale:
        return exposure.rescale_intensity(1.0 * img, in_range=(v_min, v_max))
    else:
        return img

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

if __name__ == "__main__":
    args = parse_args()
    if args.rgb:
        image = io.imread(args.src, as_gray=args.bw)
        if args.positive:
            rgb = image
        else:
            rgb = exposure.adjust_gamma(util.invert(image), gamma=2.222)
    else:
        raw = rawpy.imread(args.src)
        if args.linearraw:
            gamma = (1.0, 1.0)
        else:
            gamma = (args.rawgamma, 4.5)
        rgb = raw.postprocess(gamma=gamma,
                                half_size=False,
                                demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
                                dcb_enhance=True,
                                no_auto_bright=not args.useautobrightness,
                                auto_bright_thr=0.01,
                                use_camera_wb=False,
                                use_auto_wb=args.useautowb,
                                output_color=rawpy.ColorSpace.raw,
                                output_bps=16)

    img_src = rgb
 
    if args.noadapt:
        if args.withoutrescale:
            contrasted = util.img_as_uint(img_src)
        elif args.globalrescale:
            contrasted = rescale_intensity(img_src)
        else:
            b, g, r = cv2.split(img_src)
            contrasted = cv2.merge((
                rescale_intensity(b),
                rescale_intensity(g),
                rescale_intensity(r)))
        if args.bw:
            contrasted = util.invert(rgb2gray(contrasted))
        elif args.bwhsv:
            contrasted = util.invert(rgb2gray_hsv(contrasted))
        elif args.bwitur:
            contrasted = util.invert(rgb2gray_itur(contrasted))
        elif not args.positive:
            contrasted = util.invert(contrasted)
    elif args.globalrescale or args.bwitur:
        b, g, r = cv2.split(img_src)
        r_c = adaptive_hist(r)
        g_c = adaptive_hist(g)
        b_c = adaptive_hist(b)
        if args.positive:
            contrasted = rescale_intensity(cv2.merge((b_c, g_c, r_c)))
        else:
            contrasted = util.invert(rescale_intensity(cv2.merge((b_c, g_c, r_c))))
            if args.bwitur:
                contrasted = rgb2gray_itur(contrasted)
    elif args.bw or args.bwhsv or args.bwitur:
        if args.bw:         # for bnw films
            gray = rgb2gray(img_src)
        elif args.bwhsv:
            gray = rgb2gray_hsv(img_src)
        elif args.bwitur:
            gray = rgb2gray_itur(img_src)
        contrasted = util.invert(rescale_intensity(adaptive_hist(gray)))
    else:
        b, g, r = cv2.split(img_src)
        r_c = rescale_intensity(adaptive_hist(r))
        g_c = rescale_intensity(adaptive_hist(g))
        b_c = rescale_intensity(adaptive_hist(b))
        if args.positive:
            contrasted = cv2.merge((b_c, g_c, r_c))
        else:
            contrasted = util.invert(cv2.merge((b_c, g_c, r_c)))

    result = exposure.adjust_gamma(contrasted, gamma=args.gamma)

    if args.out:
        io.imsave(os.path.abspath(args.out), util.img_as_uint(result), check_contrast=False, plugin='pil')
    else:
        io.imshow(result)
        io.show()
