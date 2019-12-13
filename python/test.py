#!/usr/bin/python
import os, sys
import rawpy
import imageio
from PIL import Image
import PIL.ImageOps
import cv2
import numpy as np

def gamma(gamma_r, gamma_g, gamma_b, gain_r=1.0, gain_g=1.0, gain_b=1.0):
    r_tbl = [min(255, int((x / 255.) ** (1. / gamma_r) * gain_r * 255.)) for x in range(256)]
    g_tbl = [min(255, int((x / 255.) ** (1. / gamma_g) * gain_g * 255.)) for x in range(256)]
    b_tbl = [min(255, int((x / 255.) ** (1. / gamma_b) * gain_b * 255.)) for x in range(256)]
    return r_tbl + g_tbl + b_tbl

def cv2_gamma(gamma, bit=8):
    table = np.empty((1, 2 ** bit), np.uint16)
    for i in range(2 ** bit):
        table[0, i] = np.clip(pow(i / float(2 ** bit), gamma) * float(2 ** bit), 0, 2 ** bit)
    return table

raw = rawpy.imread(sys.argv[1])
rgb = raw.postprocess(gamma=(1, 1), no_auto_bright=False, use_camera_wb=False, use_auto_wb=True, output_bps=16)

# read image from array
#image = Image.fromarray(rgb)
image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

# invert image
#imageBox = image.getbbox()
#cropped = image.crop(imageBox)
#inverted = PIL.ImageOps.invert(cropped)
inverted = cv2.bitwise_not(image)
#inverted = rgb

# gamma correction
GAMMA = 1.2
#GAMMA = 1.0 
#gamma_img = contrasted.point(gamma(GAMMA, GAMMA, GAMMA))
#gamma_img.save('out.tif')
#rgb_gamma = cv2.LUT(inverted, cv2_gamma(GAMMA))
lut_table = cv2_gamma(GAMMA, bit=16)
rgb_gamma = np.empty_like(inverted)
rangex, rangey, dim = rgb_gamma.shape
for x in range(rangex):
    for y in range(rangey):
        rgb_gamma[x, y] = lut_table[0, inverted[x, y]]
#rgb_gamma = inverted

# auto contrast
#contrasted = PIL.ImageOps.autocontrast(inverted, cutoff=1)
#img_yuv = cv2.cvtColor(rgb_gamma, cv2.COLOR_BGR2YUV)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
#img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
#img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])
#contrasted = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
if len(rgb_gamma.shape) == 3:
    for channel in range(0, 3):
        rgb_gamma[:, :, channel] = clahe.apply(rgb_gamma[:, :, channel])
else:
    rgb_gamma[:, :, 0] = clahe.apply(rgb_gamma[:, :, 0])
contrasted = rgb_gamma

result = contrasted
height = result.shape[0]
width = result.shape[1]
#cv2.imwrite('out.tif', result)
cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
cv2.imshow('image', cv2.resize(result, (width // 4, height // 4)))
cv2.waitKey(0)
