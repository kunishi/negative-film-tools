#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.jpg

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -W -g 1 1 -H 1 -T -q 3 "${SRC}" | \
	magick tif:- \
		-set colorspace rgb \
		-define quantum:format=floating-point \
		-depth 16 \
		-shave 20x20 \
		-colorspace rgb \
		-channel rgb,sync \
		-auto-gamma \
		-contrast-stretch 0.2%x0% \
		-negate \
		-channel rgb,sync \
		-modulate 100,140,100 \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
