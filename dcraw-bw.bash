#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.HEIC

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -W -T -q 3 "${SRC}" | \
	magick tif:- \
		-depth 16 \
		-shave 20x20 \
		-set colorspace srgb \
		-channel rgb,!sync -auto-gamma -channel rgb,sync \
		-gamma 2.4 \
		-auto-level \
		-contrast-stretch 0.3%,0% \
		-negate \
		-colorspace lab \
			-channel r,!sync -contrast-stretch 0.2%,0% \
			+level 5%,100% \
			-sigmoidal-contrast 2,90% \
			-channel r -separate \
		-colorspace gray \
		-profile $(dirname $0)/Display_P3.icc \
		-depth 10 \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
