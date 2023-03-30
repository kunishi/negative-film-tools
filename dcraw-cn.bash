#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.webp

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -W -T -q 3 "${SRC}" | \
	magick tif:- \
		-depth 16 \
		-shave 20x20 \
		-set colorspace srgb \
		-channel rgb -auto-gamma -channel rgb,sync \
		-contrast-stretch 0.01%x0% \
		-linear-stretch 0%x0.03% \
		-sigmoidal-contrast 3,50% \
		-negate \
		-gamma 1.3 \
		-modulate 100,115,100 \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
