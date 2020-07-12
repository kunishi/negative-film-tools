#!/bin/bash

SRC=$1
DST=$2
BASE=`basename "$1" .dng`

convert "${SRC}" -colorspace rgb ${BASE}.mpc
convert ${BASE}.mpc -channel r -separate ${BASE}_r.mpc
convert ${BASE}.mpc -channel g -separate ${BASE}_g.mpc
convert ${BASE}.mpc -channel b -separate ${BASE}_b.mpc

convert ${BASE}_r.mpc -auto-gamma ${BASE}_clahe_r.mpc
convert ${BASE}_g.mpc -auto-gamma ${BASE}_clahe_g.mpc
convert ${BASE}_b.mpc -auto-gamma ${BASE}_clahe_b.mpc

convert ${BASE}_clahe_r.mpc ${BASE}_clahe_g.mpc ${BASE}_clahe_b.mpc -channel rgb -combine ${BASE}_clahe.mpc
convert ${BASE}_clahe.mpc -normalize -colorspace srgb "${DST}"

rm -f ${BASE}*.mpc ${BASE}*.cache
