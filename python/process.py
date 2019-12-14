#!/usr/bin/python
import os, sys
import rawpy
import cv2
import numpy as np
from skimage import color, exposure, io, util

raw = rawpy.imread(sys.argv[1])
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
if len(image.shape) == 3:
    rgb_gamma = exposure.adjust_gamma(inverted, gamma=1.8)
    r, g, b = cv2.split(rgb_gamma)
    r_c = exposure.rescale_intensity(r)
    g_c = exposure.rescale_intensity(g)
    b_c = exposure.rescale_intensity(b)
    contrasted = cv2.merge((r_c, g_c, b_c))
else:
    rgb_gamma = exposure.adjust_gamma(inverted, gamma=2.8)
    contrasted = exposure.equalize_hist(rgb_gamma)
    #contrasted = rgb_gamma

result = contrasted
if len(sys.argv) == 2:
    io.imshow((result / 255).astype('uint8'))
    io.show()
elif len(sys.argv) == 3:
    io.imsave(os.path.abspath(sys.argv[2]), result)
