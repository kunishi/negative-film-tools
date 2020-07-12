#!/bin/bash

SRC=$1
DST=$2
BASE=`basename "$1" .dng`

convert "${SRC}" -gamma 2.222 -set colorspace lineargray \
  -contrast-stretch 0.1%,0.1% -negate -normalize -gamma 0.85 \
  -set colorspace gray "${DST}"

rm -f ${BASE}*.mpc ${BASE}*.cache
