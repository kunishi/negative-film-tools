#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.webp

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 1 1 -W -T -d -q 3 "${SRC}" | \
	magick tif:- \
		-define quantum:format=floating-point \
		-depth 32 \
		-shave 20x20 \
		-white-balance \
		-auto-gamma \
		-negate \
		-sigmoidal-contrast 3,50% \
		-auto-gamma \
		+sigmoidal-contrast 2,0% \
		+sigmoidal-contrast 1,100% \
		-auto-gamma \
		-auto-level \
		-linear-stretch 0.01%x0.03% \
		-sigmoidal-contrast 2,75% \
		+level 5%,95% \
		-colorspace gray \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
