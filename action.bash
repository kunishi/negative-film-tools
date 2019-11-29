#!/bin/bash

export PATH="/usr/local/bin:$PATH"

#SRC="$HOME/Downloads/Negfix8"
CWD="`pwd`"
DST="$HOME/Dropbox/Photos/Negfix8"
WORK="/tmp/Negfix8"

DONEDIR="${DST}/Done_$(date +%Y%m%d_%H%M%S)"

# fix EXIF for later processing

for f in "$@"; do
  cd "$CWD"
  if [[ -f "$f" ]]; then
    mkdir -p $DONEDIR $WORK
    cp -p "$f" "$WORK/$f" && \
      cd $WORK && \
      exiftool -overwrite_original \
        '-createdate<fileaccessdate' \
        '-modifydate<fileaccessdate' \
        '-datetimeoriginal<fileaccessdate' \
        '-exifversion=0231' \
        '-offsettime=+09:00' \
        '-offsettimeoriginal=+09:00' \
        "$WORK/$f" && \
      /usr/local/bin/negfix8 "$WORK/$f" "$WORK/P_$f" && \
      /usr/local/bin/autotone -G -n "$WORK/P_$f" "$WORK/${f%%.*}.jpg" && \
      exiftool -overwrite_original \
        -TagsFromFile "$WORK/$f" "-all:all>all:all" "${WORK}/${f%%.*}.jpg" && \
      cp -p "$WORK/${f%%.*}.jpg" $DONEDIR && \
      rm -f "$WORK/${f%%.*}.jpg" "${WORK}/$f" "${WORK}/P_$f"
  fi
done

function cleanup() {
  rm -rf "$WORK"
}

trap cleanup EXIT SIGINT
