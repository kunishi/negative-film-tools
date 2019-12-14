#!/bin/bash

TMPDIR=/tmp/process

OUTDIR=${HOME}/Dropbox/Photos/process/Done_$(date +%Y%m%d_%H%M%S)

if [ "$1" = "--bw" ]; then
  BW="$1"
  shift
fi

for arg in "$@"; do
  mkdir -p ${OUTDIR} ${TMPDIR}
  base=`basename "${arg}" .dng`
  echo ${base}
  python3 ${HOME}/git/negative-film-tools/python/process.py ${BW} --out "${TMPDIR}/${base}.tif" "${arg}"
  convert "${TMPDIR}/${base}.tif" "${OUTDIR}/${base}.jpg"
  exiftool -overwrite_original \
        -TagsFromFile "${arg}" "-all:all>all:all" \
        '-createdate<fileaccessdate' \
        '-modifydate<fileaccessdate' \
        '-datetimeoriginal<fileaccessdate' \
        '-exifversion=0231' \
        '-offsettime=+09:00' \
        '-offsettimeoriginal=+09:00' \
          "${OUTDIR}/${base}.jpg"
done
rm -rf ${TMPDIR}
