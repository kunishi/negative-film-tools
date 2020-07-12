#!/bin/bash

SRC=$1
DST=$2
BASE=`basename "$1" .dng`

convert "${SRC}" -gamma 2.222 -set colorspace srgb ${BASE}.mpc
convert ${BASE}.mpc -channel r -separate ${BASE}_r.mpc
convert ${BASE}.mpc -channel g -separate ${BASE}_g.mpc
convert ${BASE}.mpc -channel b -separate ${BASE}_b.mpc

convert ${BASE}_r.mpc -gamma 0.85 -contrast-stretch 0.1%,0.1% ${BASE}_clahe_r.mpc
convert ${BASE}_g.mpc -gamma 0.8 -contrast-stretch 0.1%,0.1% ${BASE}_clahe_g.mpc
convert ${BASE}_b.mpc -gamma 1.3 -contrast-stretch 0.1%,0.1% ${BASE}_clahe_b.mpc

convert ${BASE}_clahe_r.mpc ${BASE}_clahe_g.mpc ${BASE}_clahe_b.mpc \
  -channel rgb -combine ${BASE}_clahe.mpc
convert ${BASE}_clahe.mpc \
  -gamma 1.8 -negate -set colorspace srgb -linear-stretch 2%,1% "${DST}"

rm -f ${BASE}*.mpc ${BASE}*.cache
