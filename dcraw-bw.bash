#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.jpg

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -H 1 -T -d -q 3 "${SRC}" | \
	magick tif:- \
		-define quantum:format=floating-point \
		-depth 32 \
		-shave 20x20 \
		-colorspace srgb \
		-auto-gamma \
		-negate \
		-channel rgb \
		-auto-gamma \
		-channel rgb,sync \
		-white-balance \
		-auto-gamma \
		-gamma 1.3 \
		-colorspace LinearGray \
		-linear-stretch 0.005%x0.5% \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
