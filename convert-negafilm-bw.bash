#!/bin/bash

SRC=$1
BASE=`basename "$1" .dng`

convert "${SRC}" -gamma 2.222 -colorspace lineargray ${BASE}.mpc
convert ${BASE}.mpc -contrast-stretch 0.1%,0.1% -gamma 1.8 -negate -normalize \
  -colorspace gray ${BASE}.jpg

rm -f ${BASE}*.mpc ${BASE}*.cache
