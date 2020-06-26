#!/bin/bash

CAPTION="$1"; shift
for file in "$@"; do
  echo "$file"
  exiftool -verbose -overwrite_original_in_place \
    '-iptc:caption-abstract='"${CAPTION}" \
    '-iptc:keywords='"${CAPTION}" \
    '-subject='"${CAPTION}" \
    "$file"
done
