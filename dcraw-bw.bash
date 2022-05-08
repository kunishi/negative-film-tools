#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.jpg

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -4 -T -q 1 "${SRC}" | \
	magick tif:- \
		-depth 16 \
		-shave 20x20 \
		-colorspace srgb \
		-auto-gamma \
		-linear-stretch 0%x0.007% \
		-colorspace Gray \
		-linear-stretch 0.007%x0% \
		-negate \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
