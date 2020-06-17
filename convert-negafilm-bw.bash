#!/bin/bash

SRC=$1
BASE=`basename "$1" .dng`

convert "${SRC}" ${BASE}.mpc
convert ${BASE}.mpc -colorspace gray -auto-gamma -negate ${BASE}_clahe.mpc
convert ${BASE}_clahe.mpc -normalize -colorspace gray ${BASE}.jpg

rm -f ${BASE}*.mpc ${BASE}*.cache
