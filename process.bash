#!/bin/bash

TMPDIR=/tmp/process
PREFIX=Done
DATE=$(date +%Y%m%d_%H%M%S)
GAMMA='--gamma 1.0'
SHARPNESS="-s"
CONTRAST="-b"
AUTOGAMMA="-G"
WB="-w"
GB="-g"
ARGS=""
PYARGS=""

for arg in "$@"; do
  if [[ "${arg}" == "--gamma="* ]]; then
    ARGS="${ARGS} ${arg}"
    GAMMA=`echo "${arg}" | sed -e 's/^=/ /'`
    PYARGS="${PYARGS} ${GAMMA}"
    shift
    continue
  elif [[ "${arg}" == "--rawgamma="* ]]; then
    ARGS="${ARGS} ${arg}"
    RAWGAMMA=`echo "${arg}" | sed -e 's/^=/ /'`
    PYARGS="${PYARGS} ${RAWGAMMA}"
    shift
    continue
  elif [[ "${arg}" == "--prefix="* ]]; then
    ARGS="${ARGS} ${arg}"
    PREFIX=`echo "${arg}" | sed -e 's/^.*=//'`
    shift
    continue
  elif [[ "${arg}" == "--autotone" ]]; then
    ARGS="${ARGS} ${arg}"
    AUTOTONE=TRUE
    SHARPNESS=""
    CONTRAST=""
    AUTOGAMMA=""
    GB=""
    WB=""
    shift
    continue
  elif [[ "${arg}" == "--autocontrast" ]]; then
    ARGS="${ARGS} ${arg}"
    AUTOTONE=TRUE
    CONTRAST=""
    shift
    continue
  elif [[ "${arg}" == "--autogray" ]]; then
    ARGS="${ARGS} ${arg}"
    AUTOTONE=TRUE
    WB=""
    GB=""
    shift
    continue
  elif [[ "${arg}" == "--autogamma" ]]; then
    ARGS="${ARGS} ${arg}"
    AUTOTONE=TRUE
    AUTOGAMMA=""
    shift
    continue
  elif [[ "${arg}" == "--normalize" ]]; then
    ARGS="${ARGS} ${arg}"
    NORMALIZE='-normalize'
    shift
    continue
  elif [[ "${arg}" == "--"* ]]; then
    ARGS="${ARGS} ${arg}"
    PYARGS="${PYARGS} ${arg}"
    shift
    continue
  fi
  
  OUTDIR=${HOME}/Dropbox/Photos/process/${PREFIX}_${DATE}
  mkdir -p ${OUTDIR} ${TMPDIR}
  filename="${arg##*/}"
  base="${filename%.*}"
  echo ${base}
  echo ${ARGS} > ${OUTDIR}/opt.txt
  python3 process.py ${PYARGS} --out "${TMPDIR}/${base}.tif" "${arg}"
  if [[ "${AUTOTONE}" == "TRUE" && `/usr/bin/which -s autotone` -eq 0 ]]; then
    autotone -n -p ${SHARPNESS} ${CONTRAST} ${WB} ${GB} ${AUTOGAMMA} -GN a -WN a "${TMPDIR}/${base}.tif" "${TMPDIR}/${base}.mpc"
    convert -define jpeg:extent=7M -colorspace sRGB ${NORMALIZE} "${TMPDIR}/${base}.mpc" "${OUTDIR}/${base}.jpg"
  else
    convert -define jpeg:extent=7M -colorspace sRGB ${NORMALIZE} "${TMPDIR}/${base}.tif" "${OUTDIR}/${base}.jpg"
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
