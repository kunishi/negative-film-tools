#!/bin/bash

CAPTION="$1"; shift

IFS_bak=$IFS
IFS=','
KWOPTS=()
for kw in ${CAPTION}; do
  echo ${kw## }
  KWOPTS+=("-iptc:keywords=${kw## }")
done

for file in "$@"; do
  echo "$file"
  exiftool -verbose -overwrite_original_in_place \
    "-iptc:caption-abstract=${CAPTION}" \
    "-subject=${CAPTION}" \
    ${KWOPTS[@]} \
    "$file"
done
