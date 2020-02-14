#!/bin/bash

TMPDIR=/tmp/process
PREFIX=Done
DATE=$(date +%Y%m%d_%H%M%S)

for arg in "$@"; do
  if [[ "${arg}" == "--gamma="* ]]; then
    GAMMA=`echo "${arg}" | sed -e 's/^=/ /'`
    shift
    continue
  elif [[ "${arg}" == "--prefix="* ]]; then
    PREFIX=`echo "${arg}" | sed -e 's/^.*=//'`
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
  
  OUTDIR=${HOME}/Dropbox/Photos/process/${PREFIX}_${DATE}
  mkdir -p ${OUTDIR} ${TMPDIR}
  filename="${arg##*/}"
  base="${filename%.*}"
  echo ${base}
  python3 process.py ${ARGS} ${GAMMA} --out "${TMPDIR}/${base}.tif" "${arg}"
  if [[ "${AUTOTONE}" == "TRUE" && `/usr/bin/which -s autotone` -eq 0 ]]; then
    autotone -n -p -s -b ${AUTOGAMMA} -GN a -WN a "${TMPDIR}/${base}.tif" "${TMPDIR}/${base}.mpc"
    convert -define jpeg:extent=7M "${TMPDIR}/${base}.mpc" "${OUTDIR}/${base}.jpg"
  else
    convert -define jpeg:extent=7M "${TMPDIR}/${base}.tif" "${OUTDIR}/${base}.jpg"
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
