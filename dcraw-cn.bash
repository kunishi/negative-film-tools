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
		-negate \
		-channel rgb -auto-gamma -channel rgb,sync \
		-modulate 85,105,100 \
		-auto-level \
		-channel rgb -auto-gamma -channel rgb,sync \
		-linear-stretch 0.02%x0.02% \
		-contrast-stretch 0%x0.03% \
		-modulate 100,120,100 \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
