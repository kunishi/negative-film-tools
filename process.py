#!/usr/bin/python3
import os, sys
import argparse
import cv2
import json
import numpy as np
import pathlib
import rawpy
import shutil
import subprocess
import tempfile
from datetime import datetime
from skimage import color, exposure, io, util

def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("src", help="source RAW file", nargs='+')
    parser.add_argument("--adapt-hsv", help="apply CLAHE on value channel", action="store_true")
    parser.add_argument("--autogamma", help="apply ImageMagick autogamma", action="store_true")
    parser.add_argument("--autogamma-color", help="apply ImageMagick autogamma with each channel", action="store_true")
    parser.add_argument("--autogamma-lab", help="apply ImageMagick autogamma on Lab colorspace", action="store_true")
    parser.add_argument("--autolevel", help="apply ImageMagick autolevel", action="store_true")
    parser.add_argument("--autolevel-color", help="apply ImageMagick autolevel with each channel", action="store_true")
    parser.add_argument("--bw", help="run in bw mode", action="store_true")
    parser.add_argument("--bwitur", help="run in bw mode based on ITU-R BT.601", action="store_true")
    parser.add_argument("--bwhsv", help="run in bw mode based on HSV", action="store_true")
    parser.add_argument("--contrast-stretch", help="apply contrast stretch by using ImageMagick", action="store_true")
    parser.add_argument("--fixcaption", help="fix caption metadata", action="store_true")
    parser.add_argument("--format", help="specify save format", default=".jpg")
    parser.add_argument("--gamma", help="specify gamma value", type=float, default=1.0)
    parser.add_argument("--globalrescale", help="rescaling globally", action="store_true")
    parser.add_argument("--gray", help="apply gray profile", action="store_true")
    parser.add_argument("--imgamma", help="gamma correction by using ImageMagick", type=float)
    parser.add_argument("--imnegate", help="apply ImageMagick negate", action="store_true")
    parser.add_argument("--lineargray", help="apply linear gray profile", action="store_true")
    parser.add_argument("--linearraw", help="process RAW image without gamma correction", action="store_true")
    parser.add_argument("--linearrgb", help="apply linear rgb profile", action="store_true")
    parser.add_argument("--linear-stretch", help="apply linear stretch by using ImageMagick", action="store_true")
    parser.add_argument("--noadapt", help="run without adaptive histogram equalization", action="store_true")
    parser.add_argument("--normalize", help="apply ImageMagick normalize", action="store_true")
    parser.add_argument("--normalize-lab", help="apply ImageMagick normalize on Lab colorspace", action="store_true")
    parser.add_argument("--outdir", help="output directory")
    parser.add_argument("--prefix", help="prefix of the output subdir", default="Done")
    parser.add_argument("--positive", help="input the positive image", action="store_true")
    parser.add_argument("--rawgamma", help="specify gamma value in RAW processing", type=float, default=2.25)
    parser.add_argument("--saturate", help="compensate saturation by using ImageMagick", action="store_true")
    parser.add_argument("--strong-normalize", help="apply strong normalize by using ImageMagick", action="store_true")
    parser.add_argument("--useautobrightness", help="disable auto brightness mode in libraw", action="store_true")
    parser.add_argument("--useautowb", help="enable auto white balance mode in libraw", action="store_true")
    parser.add_argument("--withoutrescale", help="do not process rescaling", action="store_true")
    parser.add_argument("--rgb", help="input RGB image", action="store_true")
    parser.add_argument("--out", help="specify the destination TIFF file")
    return parser.parse_args()

def adaptive_hist(img):
    if not args.noadapt:
        return exposure.equalize_adapthist(img, clip_limit=0.004, kernel_size=96)
    else:
        return img

def rescale_intensity(img):
    if not args.withoutrescale:
        v_min, v_max = np.percentile(1.0 * img, (0.03, 99.97))
        print(v_min, v_max)
        return exposure.rescale_intensity(1.0 * img, in_range=(v_min, v_max))
    else:
        return img

def rgb2gray(img, gamma=1.8):
    return color.rgb2gray(img)

def rgb2gray_itur(img, gamma=1.5):
    coeffs = np.array([0.299, 0.587, 0.114], dtype=img.dtype)
    return img @ coeffs

def rgb2gray_hsv(img, gamma=1.0):
    h, s, v = cv2.split(color.rgb2hsv(img))
    return v

def imagemagick_convert_command(infile, outdir):
    command=["/usr/local/bin/convert",
             "-define", "jpeg:extent=7M",
             str(infile),
             "-colorspace", "rgb"]
    if args.autogamma:
        command.extend(["-auto-gamma"])
    if args.autogamma_color:
        command.extend(["-channel", "rgb", "-auto-gamma", "+channel"])
    if args.autogamma_lab:
        command.extend(["-colorspace", "lab", "-channel", "b", "-auto-gamma", "+channel", "-colorspace", "rgb"])
    if args.imgamma:
        command.extend(["-gamma", str(args.imgamma)])
    if args.imnegate:
        command.append("-negate")
    if args.autolevel:
        command.extend(["-colorspace", "lab", "-channel", "0", "-auto-level", "+channel", "-colorspace", "srgb"])
    if args.autolevel_color:
        command.extend(["-channel", "rgb", "-auto-level", "-channel", "rgb,sync"])
    if args.normalize:
        command.append("-normalize")
    if args.normalize_lab:
        command.extend(["-colorspace", "lab", "-channel", "0", "-normalize", "+channel", "-colorspace", "rgb"])
    if args.linear_stretch:
        command.extend(["-linear-stretch", "0.7%x0.1%"])
    if args.strong_normalize:
        command.extend(["-normalize", "-normalize"])
    if args.contrast_stretch:
        command.extend(["-contrast-stretch", "0.7%x0.02%"])
    if args.saturate:
        command.extend(["-colorspace", "hsl", "-channel", "1", "-evaluate", "multiply", "1.45", "+channel", "-colorspace", "rgb"])
    if args.gray:
        command.extend(["-colorspace", "gray", "-profile", str(pathlib.Path("./Compact-ICC-Profiles/profiles/sGrey-v4.icc"))])
    if args.lineargray:
        command.extend(["-colorspace", "lineargray", "-profile", str(pathlib.Path("./Compact-ICC-Profiles/profiles/sGrey-v4.icc"))])
    if args.linearrgb:
        command.extend(["-colorspace", "rgb", "-profile", str(pathlib.Path("./Compact-ICC-Profiles/profiles/Rec2020-v4.icc"))])
    if not(args.gray) and not(args.lineargray) and not(args.linearrgb):
        command.extend(["-colorspace", "srgb", "-profile", str(pathlib.Path("./Compact-ICC-Profiles/profiles/DisplayP3-v4.icc"))])
    command.append(str(pathlib.Path(outdir, pathlib.Path(infile).with_suffix(args.format).name)))
    return command

def exiftool_command(jpg, raw):
    command = ["/usr/local/bin/exiftool",
               "-overwrite_original_in_place"]
    command.extend(["-TagsFromFile", str(pathlib.Path(raw))])
    command.append("-all:all>all:all")
    command.append(str(pathlib.Path(jpg)))
    return command

def split_image(img, r, g, b):
    b, g, r = cv2.split(img)
    return img, r, g, b

def merge_image(img, r, g, b):
    img = cv2.merge((b, g, r))
    return img, r, g, b

def clahe(img, r, g, b):
    if args.adapt_hsv:
        h, s, v = cv2.split(color.rgb2hsv(img))
        img = color.hsv2rgb(cv2.merge((h, s, adaptive_hist(v))))
    elif args.noadapt:
        pass
    else:
        r = adaptive_hist(r)
        g = adaptive_hist(g)
        b = adaptive_hist(b)
        img = cv2.merge((b, g, r))
    return img, r, g, b

def rescale(img, r, g, b):
    if args.withoutrescale:
        pass
    elif args.globalrescale:
        h, s, v = cv2.split(color.rgb2hsv(img))
        img = color.hsv2rgb(cv2.merge((h, s, rescale_intensity(v))))
    else:
        r = rescale_intensity(r)
        g = rescale_intensity(g)
        b = rescale_intensity(b)
        img = cv2.merge((b, g, r))
    return img, r, g, b

def gamma_image(img, r, g, b):
    img = exposure.adjust_gamma(img, gamma=args.gamma)
    return img, r, g, b

def negate(img, r, g, b):
    if not args.positive:
        img = util.invert(img)
        b, g, r = cv2.split(img)
    return img, r, g, b

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            args = parse_args()
            outdir = '_'.join([args.prefix, datetime.now().strftime("%Y%m%d_%H%M%S")])
            os.makedirs(str(pathlib.Path(args.outdir, outdir)), exist_ok=True)
            with open(pathlib.Path(args.outdir, outdir).joinpath('params.json'), mode="w") as f:
                json.dump(args.__dict__, f, indent=4)
            for src in args.src:
                if args.rgb:
                    image = io.imread(src, as_gray=args.bw)
                    if args.positive:
                        rgb = image
                    else:
                        rgb = exposure.adjust_gamma(util.invert(image), gamma=2.222)
                else:
                    raw = rawpy.imread(src)
                    if args.linearraw:
                        gamma = (1.0, 1.0)
                    else:
                        gamma = (args.rawgamma, 1.0)
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

                img, r, g, b = split_image(rgb, None, None, None)
                img, r, g, b = clahe(img, r, g, b)
                img, r, g, b = rescale(img, r, g, b)
                img, r, g, b = negate(img, r, g, b)
                img, r, g, b = gamma_image(img, r, g, b)
                result = img

                os.makedirs(str(pathlib.Path(args.outdir, outdir)), exist_ok=True)
                tifffile = pathlib.Path(tmpdirname, pathlib.Path(src).with_suffix(".tif").name)
                io.imsave(str(tifffile), util.img_as_float64(result), check_contrast=False, plugin='tifffile')

                command = imagemagick_convert_command(tifffile, pathlib.Path(args.outdir, outdir))
                print(command)
                subprocess.run(command, stderr=subprocess.STDOUT)
                jpg = pathlib.Path(args.outdir, outdir, pathlib.Path(tifffile).with_suffix(args.format).name)
                command = exiftool_command(jpg, src)
                print(command)
                subprocess.run(command, stderr=subprocess.STDOUT)
        except KeyboardInterrupt:
            shutil.rmtree(tmpdirname)
