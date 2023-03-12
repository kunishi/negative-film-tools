#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.heic

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -H 5 -T -q 3 "${SRC}" | \
	magick tif:- \
		-depth 16 \
		-shave 20x20 \
		-set colorspace srgb \
		-modulate 100,105,100 \
		-negate \
		-channel rgb,sync \
		-sigmoidal-contrast 3,50% \
		-auto-gamma \
		-modulate 100,125,100 \
		+sigmoidal-contrast 2,10% \
		-linear-stretch 0%x0.04% \
		-colorspace lab \
		-channel red \
		-sigmoidal-contrast 3,50% \
		-channel rgb,sync \
		-colorspace srgb \
		-contrast-stretch 0%x0.02% \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
