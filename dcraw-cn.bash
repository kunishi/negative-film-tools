#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.heic

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -W -T -q 3 "${SRC}" | \
	magick tif:- \
		-depth 16 \
		-shave 20x20 \
		-set colorspace srgb \
		-white-balance \
		-modulate 100,105,100 \
		-negate \
		-channel rgb,sync \
		-sigmoidal-contrast 3,50% \
		-auto-gamma \
		-modulate 100,125,100 \
		-contrast-stretch 0.03%x0.07% \
		+sigmoidal-contrast 2,10% \
		-colorspace lab \
		-channel red \
		-auto-level \
		+channel \
		-colorspace srgb \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
