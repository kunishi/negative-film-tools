#!/bin/bash

SRC=$1
DST=$2
BASE=`basename "$1" .dng`

convert "${SRC}" -gamma 2.222 -set colorspace rgb ${BASE}.mpc
convert ${BASE}.mpc -channel r -separate ${BASE}_r.mpc
convert ${BASE}.mpc -channel g -separate ${BASE}_g.mpc
convert ${BASE}.mpc -channel b -separate ${BASE}_b.mpc

convert ${BASE}_r.mpc -gamma 1.0 -contrast-stretch 0.1%,0.1% ${BASE}_clahe_r.mpc
convert ${BASE}_g.mpc -gamma 0.9 -contrast-stretch 0.1%,0.1% ${BASE}_clahe_g.mpc
convert ${BASE}_b.mpc -gamma 1.3 -contrast-stretch 0.1%,0.1% ${BASE}_clahe_b.mpc

convert ${BASE}_clahe_r.mpc ${BASE}_clahe_g.mpc ${BASE}_clahe_b.mpc \
  -channel rgb -combine ${BASE}_clahe.mpc
convert ${BASE}_clahe.mpc \
  -negate -auto-gamma -linear-stretch 0.5%,0.25% -modulate 100,110,100 \
  -set colorspace srgb "${DST}"

rm -f ${BASE}*.mpc ${BASE}*.cache
