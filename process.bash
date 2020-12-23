#!/bin/bash

SCRIPT_DIR=$(cd $(dirname $0); pwd)
TMPDIR=/tmp/process
OUTDIR_BASE=${HOME}/Dropbox/Photos/process
PREFIX=Done
DATE=$(date +%Y%m%d_%H%M%S)
GAMMA='--gamma 1.0'
SHARPNESS="-s"
CONTRAST="-b"
AUTOGAMMA="-G"
WB="-w"
GB="-g"
ARGS=()
PYARGS=()
SRGB_ICC="./Compact-ICC-Profiles/profiles/sRGB-v4.icc"
GREY_ICC='./Compact-ICC-Profiles/profiles/sGrey-v4.icc'
DISPLAY_P3_ICC="./Compact-ICC-Profiles/profiles/DisplayP3-v4.icc"
PROPHOTO_ICC="./Compact-ICC-Profiles/profiles/ProPhoto-v4.icc"
COLORSPACE="-colorspace sRGB -profile ${DISPLAY_P3_ICC}"
#COLORSPACE=""

for arg in "$@"; do
  if [[ "${arg}" == "--gamma="* ]]; then
    ARGS+=(${arg})
    GAMMA=`echo "${arg}" | sed -e 's/^=/ /'`
    PYARGS+=("${GAMMA}")
    shift
    continue
  elif [[ "${arg}" == "--rawgamma="* ]]; then
    ARGS+=(${arg})
    RAWGAMMA=`echo "${arg}" | sed -e 's/^=/ /'`
    PYARGS+=("${RAWGAMMA}")
    shift
    continue
  elif [[ "${arg}" == "--outdir="* ]]; then
    OUTDIR_BASE=`echo "${arg}" | sed -e 's/^.*=//'`
    shift
    continue
  elif [[ "${arg}" == "--prefix="* ]]; then
    PREFIX=`echo "${arg}" | sed -e 's/^.*=//'`
    shift
    continue
  elif [[ "${arg}" == "--autogamma" ]]; then
    ARGS+=(${arg})
    IM_AUTOGAMMA="-auto-gamma"
    shift
    continue
  elif [[ "${arg}" == "--autogamma-color" ]]; then
    ARGS+=(${arg})
    IM_AUTOGAMMA="-channel rgb -auto-gamma -channel rgb,sync"
    shift
    continue
  elif [[ "${arg}" == "--autolevel" ]]; then
    ARGS+=(${arg})
    IM_AUTOLEVEL='-channel rgb,sync -auto-level -channel rgb,sync'
    shift
    continue
  elif [[ "${arg}" == "--autolevel-color" ]]; then
    ARGS+=(${arg})
    IM_AUTOLEVEL='-channel rgb -auto-level -channel rgb,sync'
    shift
    continue
  elif [[ "${arg}" == "--normalize" ]]; then
    ARGS+=(${arg})
    NORMALIZE='-normalize'
    shift
    continue
  elif [[ "${arg}" == "--linear-stretch" ]]; then
    ARGS+=(${arg})
    NORMALIZE='-linear-stretch 0.7%,0.4%'
    shift
    continue
  elif [[ "${arg}" == "--strong-normalize" ]]; then
    ARGS+=(${arg})
    NORMALIZE='-linear-stretch 2%,0.5%'
    shift
    continue
  elif [[ "${arg}" == "--contrast-stretch" ]]; then
    ARGS+=(${arg})
    NORMALIZE='-contrast-stretch 0.7%,0.02%'
    shift
    continue
  elif [[ "${arg}" == "--gray" ]]; then
    ARGS+=(${arg})
    COLORSPACE="-colorspace Gray -profile ${GREY_ICC}"
    shift
    continue
  elif [[ "${arg}" == "--lineargray" ]]; then
    ARGS+=(${arg})
    COLORSPACE="-colorspace LinearGray -profile ${GREY_ICC}"
    shift
    continue
  elif [[ "${arg}" == "--linearrgb" ]]; then
    ARGS+=(${arg})
    COLORSPACE="-colorspace rgb"
    shift
    continue
  elif [[ "${arg}" == "--fixcaption" ]]; then
    CAPTION=TRUE
    shift
    continue
  elif [[ "${arg}" == "--"* ]]; then
    ARGS+=(${arg})
    PYARGS+=(${arg})
    shift
    continue
  fi
  
  OUTDIR=${OUTDIR_BASE}/${PREFIX}_${DATE}
  mkdir -p ${OUTDIR}
  mkdir -p ${TMPDIR}
  filename="${arg##*/}"
  base="${filename%.*}"
  echo ${base}
  python3 process.py ${PYARGS[*]} --out "${TMPDIR}/${base}.png" "${arg}"
  convert -define jpeg:extent=7M "${TMPDIR}/${base}.png" -colorspace rgb -profile ${PROPHOTO_ICC} ${IM_AUTOGAMMA} ${IM_AUTOLEVEL} ${NORMALIZE} ${MODULATE} ${NEGATE} ${COLORSPACE} "${TMPDIR}/${base}.jpg"
  if [[ "${CAPTION}" == "TRUE" ]]; then
    exiftool -overwrite_original_in_place \
        -TagsFromFile "${arg}" "-all:all>all:all" \
        "-iptc:caption-abstract<\$iptc:caption-abstract, \$make \$model, process options: ${ARGS[*]}" \
        -colorspace=sRGB -directory="${OUTDIR}" \
          "${TMPDIR}/${base}.jpg"
  else
    exiftool -overwrite_original_in_place \
        -TagsFromFile "${arg}" "-all:all>all:all" \
        -colorspace=sRGB -directory="${OUTDIR}" \
          "${TMPDIR}/${base}.jpg"
  fi
done
rm -rf ${TMPDIR}

trap "rm -rf ${TMPDIR}" 1 2 3 15
