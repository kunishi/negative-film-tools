#!/bin/bash

SRC=$1
BASE=`basename "$1" .dng`

convert "${SRC}" -colorspace srgb ${BASE}.mpc
convert ${BASE}.mpc -channel r -separate ${BASE}_r.mpc
convert ${BASE}.mpc -channel g -separate ${BASE}_g.mpc
convert ${BASE}.mpc -channel b -separate ${BASE}_b.mpc

convert ${BASE}_r.mpc -auto-gamma -negate ${BASE}_clahe_r.mpc
convert ${BASE}_g.mpc -auto-gamma -negate ${BASE}_clahe_g.mpc
convert ${BASE}_b.mpc -auto-gamma -negate ${BASE}_clahe_b.mpc

convert ${BASE}_clahe_r.mpc ${BASE}_clahe_g.mpc ${BASE}_clahe_b.mpc \
  -channel rgb -combine ${BASE}_clahe.mpc
convert ${BASE}_clahe.mpc -define jpeg:extent=7M \
  -colorspace srgb -gamma 0.85 -linear-stretch 2%,1% ${BASE}.jpg

rm -f ${BASE}*.mpc ${BASE}*.cache
