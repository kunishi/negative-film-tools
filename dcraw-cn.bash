#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.AVIF

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -W -T -q 3 "${SRC}" | \
	magick tif:- \
		-depth 16 \
		-shave 20x20 \
		-channel rgb,!sync -auto-gamma -channel rgb,sync \
		-gamma 2.4 \
		-auto-level \
		-contrast-stretch 0.3%,0% \
		-linear-stretch 0%,0.2% \
		-negate \
		-modulate 100,130,100 \
		-profile $(dirname $0)/Display_P3.icc \
		-depth 10 \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
