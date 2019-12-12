#!/usr/bin/python
import os, sys
import rawpy
import imageio
from PIL import Image
import PIL.ImageOps

raw = rawpy.imread("Film127_11.dng")
rgb = raw.postprocess(use_auto_wb=True)
#inverted = (255 - rgb)
#imageio.imsave('Film150_11.tiff', inverted)

image = Image.fromarray(rgb)
inverted = PIL.ImageOps.invert(image)
contrasted = PIL.ImageOps.autocontrast(inverted)
contrasted.save('Film127_11.tiff')
