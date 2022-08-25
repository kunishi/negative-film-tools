#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.jpg

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -W -g 2.4 12.92 -H 1 -T -q 3 "${SRC}" | \
	magick tif:- \
		-define quantum:format=floating-point \
		-depth 32 \
		-shave 20x20 \
		-channel rgb,sync \
		-auto-gamma \
		-negate \
		-contrast-stretch 0%x0.2% \
		-gamma 0.8 \
		-white-balance \
		-modulate 100,150,100 \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
