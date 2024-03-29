#!/usr/bin/python3
import os
import sys
import argparse
import json
import numpy as np
import pathlib
import piexif
import rawpy
import shutil
import subprocess
import tempfile
from datetime import datetime
from skimage import color, exposure, io, util


def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("src", help="source RAW file", nargs='+')
    parser.add_argument(
        "--adapt-hsv", help="apply CLAHE on value channel", action="store_true")
    parser.add_argument(
        "--autogamma", help="apply ImageMagick autogamma", action="store_true")
    parser.add_argument(
        "--autogamma-color", help="apply ImageMagick autogamma with each channel", action="store_true")
    parser.add_argument(
        "--autogamma-lab", help="apply ImageMagick autogamma on Lab colorspace", action="store_true")
    parser.add_argument(
        "--autogamma-xyz", help="apply Imagemagick autogamma on XYZ colorspace", action="store_true")
    parser.add_argument(
        "--autolevel", help="apply ImageMagick autolevel", action="store_true")
    parser.add_argument(
        "--autolevel-color", help="apply ImageMagick autolevel with each channel", action="store_true")
    parser.add_argument(
        "--autolevel-lab", help="apply ImageMagick autolevel on Lab colorspace", action="store_true")
    parser.add_argument(
        "--autolevel-xyz", help="apply ImageMagick autolevel on XYZ colorspace", action="store_true")
    parser.add_argument(
        "--blue-filter", help="apply B filter", action="store_true")
    parser.add_argument(
        "--contrast", help="apply contrast by using ImageMagick", action="store_true")
    parser.add_argument(
        "--contrast-stretch", help="apply contrast stretch by using ImageMagick", action="store_true")
    parser.add_argument(
        "--fixcaption", help="fix caption metadata", action="store_true")
    parser.add_argument("--format", help="specify save format", default=".jpg")
    parser.add_argument("--gamma", help="specify gamma value",
                        type=float, default=1.0)
    parser.add_argument("--globalrescale",
                        help="rescaling globally", action="store_true")
    parser.add_argument("--gray", help="apply gray profile",
                        action="store_true")
    parser.add_argument(
        "--imgamma", help="gamma correction by using ImageMagick", type=float)
    parser.add_argument(
        "--imnegate", help="apply ImageMagick negate", action="store_true")
    parser.add_argument(
        "--imscript", help="apply ImageMagick script", type=str)
    parser.add_argument(
        "--lineargray", help="apply linear gray profile", action="store_true")
    parser.add_argument(
        "--linearraw", help="process RAW image without gamma correction", action="store_true")
    parser.add_argument(
        "--linearrgb", help="apply linear rgb profile", action="store_true")
    parser.add_argument(
        "--linear-stretch", help="apply linear stretch by using ImageMagick", action="store_true")
    parser.add_argument(
        "--luminance-gray", help="convert to grayscale of only luminance channel", action="store_true")
    parser.add_argument(
        "--noadapt", help="run without adaptive histogram equalization", action="store_true")
    parser.add_argument(
        "--normalize", help="apply ImageMagick normalize", action="store_true")
    parser.add_argument(
        "--normalize-color", help="apply ImageMagick normalize on each RGB channels", action="store_true")
    parser.add_argument(
        "--normalize-lab", help="apply ImageMagick normalize on Lab colorspace", action="store_true")
    parser.add_argument(
        "--normalize-xyz", help="apply ImageMagick normalize on XYZ colorspace", action="store_true")
    parser.add_argument("--outdir", help="output directory")
    parser.add_argument(
        "--prefix", help="prefix of the output subdir", default="Done")
    parser.add_argument(
        "--positive", help="input the positive image", action="store_true")
    parser.add_argument(
        "--rawgamma", help="specify gamma value in RAW processing", type=float, default=2.222)
    parser.add_argument(
        "--red-filter", help="apply R filter", action="store_true")
    parser.add_argument(
        "--saturate", help="compensate saturation by using ImageMagick", action="store_true")
    parser.add_argument("--sigmoidal-contrast",
                        help="apply ImageMagick sigmoidal contrast")
    parser.add_argument(
        "--strong-normalize", help="apply strong normalize by using ImageMagick", action="store_true")
    parser.add_argument("--useautobrightness",
                        help="disable auto brightness mode in libraw", action="store_true")
    parser.add_argument(
        "--useautowb", help="enable auto white balance mode in libraw", action="store_true")
    parser.add_argument(
        "--white-balance", help="apply ImageMagick white-balance", action="store_true")
    parser.add_argument("--withoutrescale",
                        help="do not process rescaling", action="store_true")
    parser.add_argument("--rgb", help="input RGB image", action="store_true")
    parser.add_argument("--out", help="specify the destination TIFF file")
    return parser.parse_args()


def get_exif_orientation(img):
    exif_dict = piexif.load(img)
    if piexif.ImageIFD.Orientation in exif_dict["0th"]:
        return exif_dict["0th"][piexif.ImageIFD.Orientation]
    else:
        return 1


def convert_to_rawpy_flip(orientation):
    orientation_to_flip = {
        1: 0,
        2: 1,
        3: 3,
        4: 2,
        5: 4,
        6: 5,
        7: 7,
        8: 6
    }
    return orientation_to_flip[orientation]


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


def imagemagick_convert_command(infile, outdir):
    commands = [
        "/opt/homebrew/bin/magick",
        "/usr/local/bin/magick",
        "/usr/bin/magick"
    ]
    convert_command = ""
    for c in commands:
        if os.path.exists(c):
            convert_command = c
            break
    command = [convert_command,
               str(infile)]
    if args.imscript:
        with open(args.imscript, "r") as f:
            for line in f:
                command.extend(line.split())
    else:
        command.extend(["-colorspace", "rgb"])

    if args.autogamma:
        command.extend(["-auto-gamma"])
    if args.autogamma_color:
        command.extend(["-channel", "rgb", "-auto-gamma", "+channel"])
    if args.autogamma_lab:
        command.extend(["-colorspace", "lab", "-channel", "0",
                       "-auto-gamma", "+channel", "-colorspace", "rgb"])
    if args.autogamma_xyz:
        command.extend(
            ["-colorspace", "xyz", "-auto-gamma", "-colorspace", "rgb"])
    if args.imgamma:
        command.extend(["-channel", "ALL,sync", "-gamma", str(args.imgamma)])
    if args.imnegate:
        command.append("-negate")
    if args.white_balance:
        command.append("-white-balance")
    if args.autolevel:
        command.extend(["-auto-level"])
    if args.autolevel_color:
        command.extend(
            ["-channel", "rgb", "-auto-level", "-channel", "rgb,sync"])
    if args.autolevel_lab:
        command.extend(["-colorspace", "lab", "-channel", "0",
                       "-auto-level", "+channel", "-colorspace", "rgb"])
    if args.autolevel_xyz:
        command.extend(
            ["-colorspace", "xyz", "-auto-level", "-colorspace", "rgb"])
    if args.normalize:
        command.extend(["-channel", "rgb,sync", "-normalize", "+channel"])
    if args.normalize_color:
        command.extend(["-channel", "rgb", "-normalize", "+channel"])
    if args.normalize_lab:
        command.extend(["-colorspace", "lab", "-channel", "0",
                       "-normalize", "+channel", "-colorspace", "rgb"])
    if args.normalize_xyz:
        command.extend(
            ["-colorspace", "xyz", "-normalize", "-colorspace", "rgb"])
    if args.linear_stretch:
        command.extend(["-channel", "ALL,sync", "-linear-stretch", "0%,0.01%"])
    if args.strong_normalize:
        command.extend(["-normalize", "-normalize"])
    if args.contrast:
        command.extend(["-channel", "ALL,sync", "-contrast"])
    if args.contrast_stretch:
        command.extend(["-channel", "ALL", "-contrast-stretch", "0.01%,0.0%"])
    if args.sigmoidal_contrast:
        command.extend(["+sigmoidal-contrast", args.sigmoidal_contrast])
    if args.saturate:
        command.extend(["-colorspace", "hsb", "-channel", "1", "-evaluate",
                       "multiply", "1.3", "+channel", "-colorspace", "rgb"])
    if args.blue_filter:
        command.extend(["-colorspace", "rgb", "-channel-fx",
                       "'blue = 100%'", "-channel", "rgb"])
    if args.red_filter:
        command.extend(["-colorspace", "rgb", "-channel-fx",
                       "'red = 10%'", "-channel", "rgb"])

    if args.gray:
        command.extend(["-colorspace", "gray", "-profile",
                       str(pathlib.Path("./Compact-ICC-Profiles/profiles/sGrey-v4.icc"))])
    elif args.lineargray:
        command.extend(["-colorspace", "lineargray", "-profile",
                       str(pathlib.Path("./Compact-ICC-Profiles/profiles/sGrey-v4.icc"))])
    elif args.luminance_gray:
        command.extend(["-colorspace", "lab", "-channel", "0", "-separate", "-profile",
                       str(pathlib.Path("./Compact-ICC-Profiles/profiles/sGrey-v4.icc"))])
    elif args.linearrgb:
        command.extend(["-colorspace", "rgb", "-profile",
                       str(pathlib.Path("./Compact-ICC-Profiles/profiles/Rec2020-v4.icc"))])
    else:
        command.extend(["-colorspace", "srgb", "-profile",
                       str(pathlib.Path("./Compact-ICC-Profiles/profiles/DisplayP3-v4.icc"))])

    command.append(
        str(pathlib.Path(outdir, pathlib.Path(infile).with_suffix(args.format).name)))
    return command


def exiftool_command(jpg, raw):
    commands = [
        "/opt/homebrew/bin/exiftool",
        "/usr/local/bin/exiftool",
        "/usr/bin/exiftool"
    ]
    exiftool_command = ""
    for c in commands:
        if os.path.exists(c):
            exiftool_command = c
            break
    command = [exiftool_command,
               "-overwrite_original_in_place"]
    command.extend(["-TagsFromFile", str(pathlib.Path(raw))])
    command.append("-all:all>all:all")
    command.append("-orientation#=1")
    command.append(str(pathlib.Path(jpg)))
    return command


def read_img(imagefile):
    with io.imread(imagefile, as_gray=args.rw) as image:
        if args.positive:
            rgb = image
        else:
            rgb = exposure.adjust_gamma(util.invert(image), gamma=2.222)
        return rgb


def process_raw(rawfile):
    if args.linearraw:
        gamma = (1.0, 1.0)
    else:
        gamma = (args.rawgamma, 4.5)
    with rawpy.imread(rawfile) as raw:
        flip = convert_to_rawpy_flip(get_exif_orientation(rawfile))
        rgb = raw.postprocess(gamma=gamma,
                              half_size=False,
                              demosaic_algorithm=rawpy.DemosaicAlgorithm.DHT,
                              dcb_enhance=True,
                              four_color_rgb=True,
                              no_auto_bright=not args.useautobrightness,
                              no_auto_scale=False,
                              auto_bright_thr=0.0,
                              use_camera_wb=not args.useautowb,
                              use_auto_wb=args.useautowb,
                              user_flip=flip,
                              output_color=rawpy.ColorSpace.raw,
                              output_bps=16)
    return rgb


def clahe(img):
    if args.noadapt:
        pass
    elif args.adapt_hsv:
        hsv_img = color.rgb2hsv(img)
        hsv_img[:, :, 2] = adaptive_hist(hsv_img[:, :, 2])
        img = color.hsv2rgb(hsv_img)
    else:
        tmp = img.copy()
        img = np.stack([
            adaptive_hist(tmp[:, :, 0]),
            adaptive_hist(tmp[:, :, 1]),
            adaptive_hist(tmp[:, :, 2])
        ], axis=-1)
    return img


def rescale(img):
    if args.withoutrescale:
        pass
    elif args.globalrescale:
        hsv_img = color.rgb2hsv(img)
        hsv_img[:, :, 2] = rescale_intensity(hsv_img[:, :, 2])
        img = color.hsv2rgb(hsv_img)
    else:
        tmp = img.copy()
        img = np.stack([
            rescale_intensity(tmp[:, :, 0]),
            rescale_intensity(tmp[:, :, 1]),
            rescale_intensity(tmp[:, :, 2])
        ], axis=-1)
    return img


def gamma_image(img):
    return exposure.adjust_gamma(img, gamma=args.gamma)


def negate(img):
    if not args.positive:
        return util.invert(img)
    else:
        return img


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            args = parse_args()
            outdir = '_'.join(
                [args.prefix, datetime.now().strftime("%Y%m%d_%H%M%S")])
            os.makedirs(str(pathlib.Path(args.outdir, outdir)), exist_ok=True)
            with open(pathlib.Path(args.outdir, outdir).joinpath('params.json'), mode="w") as f:
                json.dump(args.__dict__, f, indent=4)
            for src in args.src:
                if args.rgb:
                    img = read_img(src)
                else:
                    img = process_raw(src)

                img = negate(img)
                img = clahe(img)
                img = rescale(img)
                img = gamma_image(img)
                result = img

                os.makedirs(str(pathlib.Path(args.outdir, outdir)),
                            exist_ok=True)
                tifffile = pathlib.Path(
                    tmpdirname, pathlib.Path(src).with_suffix(".tif").name)
                io.imsave(str(tifffile), util.img_as_float64(result),
                          check_contrast=False, plugin='tifffile')

                command = imagemagick_convert_command(
                    tifffile, pathlib.Path(tmpdirname))
                print(command)
                subprocess.run(command, stderr=subprocess.STDOUT)
                jpg = pathlib.Path(tmpdirname, pathlib.Path(
                    tifffile).with_suffix(args.format).name)
                command = exiftool_command(jpg, src)
                print(command)
                subprocess.run(command, stderr=subprocess.STDOUT)
                shutil.move(str(jpg), str(pathlib.Path(args.outdir, outdir)))
        except KeyboardInterrupt:
            shutil.rmtree(tmpdirname)
