#!/bin/bash

SRC=$1
DSTDIR=$2
DST=`basename "${SRC}" .dng`.AVIF

[ ! -d "${DSTDIR}" ] && mkdir -p "${DSTDIR}"
cd "${DSTDIR}" && \
	dcraw -v -c -o 0 -6 -g 2.4 12.92 -H 2 -T -q 3 "${SRC}" | \
	magick tif:- \
		-define quantum:format=floating-point \
		-depth 16 \
		-shave 20x20 \
		-profile $(dirname $0)/Display_P3.icc \
		-depth 10 \
		"${DST}" && \
exiftool -overwrite_original_in_place -TagsFromFile "${SRC}" \
	'-all:all>all:all' '-orientation#=1' "${DST}"
