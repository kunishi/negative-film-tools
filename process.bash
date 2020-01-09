#!/bin/bash

TMPDIR=/tmp/process

OUTDIR=${HOME}/Dropbox/Photos/process/Done_$(date +%Y%m%d_%H%M%S)


for arg in "$@"; do
  if [[ "${arg}" == "--gamma="* ]]; then
    shift
    GAMMA=`echo "${arg}" | sed -e 's/=/ /'`
    shift
    continue
  elif [[ "${arg}" == "--autotone" ]]; then
    AUTOTONE=TRUE
    shift
    continue
  elif [[ "${arg}" == "--autogray" ]]; then
    AUTOTONE=TRUE
    AUTOGAMMA="-G"
    shift
    continue
  elif [[ "${arg}" == "--"* ]]; then
    ARGS="${ARGS} ${arg}"
    shift
    continue
  fi
  mkdir -p ${OUTDIR} ${TMPDIR}
  base=`basename "${arg}" .dng`
  echo ${base}
  python3 process.py ${ARGS} ${GAMMA} --out "${TMPDIR}/${base}.tif" "${arg}"
  if [[ "${AUTOTONE}" == "TRUE" && `/usr/bin/which -s autotone` -eq 0 ]]; then
    autotone -n -p -s -b ${AUTOGAMMA} -GN a -WN a "${TMPDIR}/${base}.tif" "${OUTDIR}/${base}.jpg"
  else
    convert "${TMPDIR}/${base}.tif" "${OUTDIR}/${base}.jpg"
  fi
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
