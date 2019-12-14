#!/bin/bash

TMPDIR=/tmp/process

OUTDIR=${HOME}/Dropbox/Photos/process/Done_$(date +%Y%m%d_%H%M%S)


for arg in "$@"; do
  if [[ "${arg}" == "--bw" ]]; then
    BW="${arg}"
    shift
    continue
  elif [[ "${arg}" == "--gamma="* ]]; then
    shift
    GAMMA=`echo "${arg}" | sed -e 's/=/ /'`
    shift
    continue
  fi
  mkdir -p ${OUTDIR} ${TMPDIR}
  base=`basename "${arg}" .dng`
  echo ${base}
  python3 ${HOME}/git/negative-film-tools/python/process.py ${BW} ${GAMMA} --out "${TMPDIR}/${base}.tif" "${arg}"
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