#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.jpg

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -4 -T -q 1 "${SRC}" | \
	magick tif:- \
		-define quantum:format=floating-point \
		-depth 16 \
		-shave 20x20 \
		-colorspace srgb \
		-channel rgb,sync \
		-auto-gamma \
		-normalize \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
