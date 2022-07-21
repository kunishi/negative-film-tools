#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.jpg

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -a -H 2 -T -q 1 "${SRC}" | \
	magick tif:- \
		-set colorspace rgb \
		-define quantum:format=floating-point \
		-depth 16 \
		-shave 20x20 \
		-channel rgb \
		-auto-gamma \
		-white-balance \
		-auto-level \
		-modulate 100,120,100 \
		-negate \
		-colorspace srgb \
		-normalize \
		-white-balance \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
