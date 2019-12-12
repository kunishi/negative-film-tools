#!/usr/bin/python
import os, sys
import rawpy
import imageio
from PIL import Image
import PIL.ImageOps
import numpy as np

def gamma(gamma_r, gamma_g, gamma_b, gain_r=1.0, gain_g=1.0, gain_b=1.0):
    r_tbl = [min(255, int((x / 255.) ** (1. / gamma_r) * gain_r * 255.)) for x in range(256)]
    g_tbl = [min(255, int((x / 255.) ** (1. / gamma_g) * gain_g * 255.)) for x in range(256)]
    b_tbl = [min(255, int((x / 255.) ** (1. / gamma_b) * gain_b * 255.)) for x in range(256)]
    return r_tbl + g_tbl + b_tbl

GAMMA = 1.15

raw = rawpy.imread(sys.argv[1])
rgb = raw.postprocess(use_auto_wb=True)
image = Image.fromarray(rgb)
imageBox = image.getbbox()
cropped = image.crop(imageBox)
inverted = PIL.ImageOps.invert(cropped)
contrasted = PIL.ImageOps.autocontrast(inverted)
gamma_img = contrasted.point(gamma(GAMMA, GAMMA, GAMMA))
gamma_img.save('out.tif')
