#!/bin/bash

export PATH="/usr/local/bin:$PATH"

SRC="$HOME/Downloads/Negfix8"
DST="$HOME/Dropbox/Photos/Negfix8"
WORK="/tmp/Negfix8"

DONEDIR="${DST}/Done_$(date +%Y%m%d_%H%M%S)"

for f in "$@"; do
  if [[ ( $f == *.tif ) || ( $f == *.tiff ) || ( $f == *.TIF ) || ( $f == *.TIFF ) ]]; then
    mkdir -p $DONEDIR $WORK
    /usr/local/bin/negfix8 "$SRC/$f" "$WORK/$f" && \
      /usr/local/bin/autotone -G -n "$WORK/$f" "$WORK/${f%%.*}.jpg" && \
      cp -p "$WORK/${f%%.*}.jpg" $DONEDIR && \
      rm -f "$SRC/$f" "$WORK/${f%%.*}.jpg" "${WORK}/$f"
  fi
done

#rm -rf "$WORK"
