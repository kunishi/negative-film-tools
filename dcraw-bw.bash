#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.jpg

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -W -T -d -q 3 "${SRC}" | \
	magick tif:- \
		-define quantum:format=floating-point \
		-depth 32 \
		-shave 20x20 \
		-auto-gamma \
		-auto-level \
		-auto-gamma \
		-negate \
		-colorspace lineargray \
		-linear-stretch 0%x0.05% \
		+sigmoidal-contrast 2,50% \
		+sigmoidal-contrast 2,50% \
		-gamma 1.3 \
		-linear-stretch 0.01%x0% \
		+level 1,96% \
		-sigmoidal-contrast 3,20% \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
