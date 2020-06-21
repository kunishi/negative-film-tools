#!/bin/bash

SRC=$1
BASE=`basename "$1" .dng`

convert "${SRC}" -colorspace gray ${BASE}.mpc
convert ${BASE}.mpc -auto-gamma -normalize -negate \
  -colorspace gray -gamma 0.85 ${BASE}.jpg

rm -f ${BASE}*.mpc ${BASE}*.cache
