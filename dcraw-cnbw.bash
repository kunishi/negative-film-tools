#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.jpg

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -W -T -q 3 "${SRC}" | \
	magick tif:- \
		-define quantum:format=floating-point \
		-depth 32 \
		-shave 20x20 \
		-set colorspace srgb \
		-colorspace rgb \
		-auto-gamma \
		-auto-level \
		-colorspace lab \
		-channel red \
		-auto-level \
		-auto-gamma \
		+channel \
		-negate \
		-colorspace gray \
		-sigmoidal-contrast 3,50% \
		-gamma 0.75 \
		-linear-stretch 0%x0.01% \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"