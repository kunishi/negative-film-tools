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
ARGS=""
PYARGS=""
COLORSPACE="-colorspace sRGB"

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
  elif [[ "${arg}" == "--outdir="* ]]; then
    OUTDIR_BASE=`echo "${arg}" | sed -e 's/^.*=//'`
    shift
    continue
  elif [[ "${arg}" == "--prefix="* ]]; then
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
    GB=""
    shift
    continue
  elif [[ "${arg}" == "--autowhite" ]]; then
    ARGS="${ARGS} ${arg}"
    AUTOTONE=TRUE
    WB=""
    shift
    continue
  elif [[ "${arg}" == "--autogamma" ]]; then
    ARGS="${ARGS} ${arg}"
    #AUTOTONE=TRUE
    #AUTOGAMMA=""
    IM_AUTOGAMMA="-negate -auto-gamma -negate"
    shift
    continue
  elif [[ "${arg}" == "--autogamma-color" ]]; then
    ARGS="${ARGS} ${arg}"
    IM_AUTOGAMMA="-negate -channel rgb -auto-gamma -channel rgb,sync -negate"
    shift
    continue
  elif [[ "${arg}" == "--autolevel" ]]; then
    ARGS="${ARGS} ${arg}"
    NORMALIZE='-channel rgb -auto-level -channel rgb,sync'
    shift
    continue
  elif [[ "${arg}" == "--normalize" ]]; then
    ARGS="${ARGS} ${arg}"
    NORMALIZE='-normalize'
    shift
    continue
  elif [[ "${arg}" == "--linear-stretch" ]]; then
    ARGS="${ARGS} ${arg}"
    NORMALIZE='-linear-stretch 0.7%,0.4%'
    shift
    continue
  elif [[ "${arg}" == "--strong-normalize" ]]; then
    ARGS="${ARGS} ${arg}"
    NORMALIZE='-linear-stretch 2%,0.5%'
    shift
    continue
  elif [[ "${arg}" == "--contrast-stretch" ]]; then
    ARGS="${ARGS} ${arg}"
    NORMALIZE='-contrast-stretch 0.7%,0.02%'
    shift
    continue
  elif [[ "${arg}" == "--gray" ]]; then
    ARGS="${ARGS} ${arg}"
    COLORSPACE="-colorspace Gray"
    shift
    continue
  elif [[ "${arg}" == "--lineargray" ]]; then
    ARGS="${ARGS} ${arg}"
    COLORSPACE="-colorspace LinearGray"
    shift
    continue
  elif [[ "${arg}" == "--imagemagick" ]]; then
    ARGS="${ARGS} ${arg}"
    IM=TRUE
    IM_SCRIPT="convert-negafilm-color.bash"
    shift
    continue
  elif [[ "${arg}" == "--imagemagick-warm" ]]; then
    ARGS="${ARGS} ${arg}"
    IM=TRUE
    IM_SCRIPT="convert-negafilm-color-warm.bash"
    shift
    continue
  elif [[ "${arg}" == "--imagemagick-cold" ]]; then
    ARGS="${ARGS} ${arg}"
    IM=TRUE
    IM_SCRIPT="convert-negafilm-color-cold.bash"
    shift
    continue
  elif [[ "${arg}" == "--imagemagick-bw" ]]; then
    ARGS="${ARGS} ${arg}"
    IM=TRUE
    IM_SCRIPT="convert-negafilm-bw.bash"
    shift
    continue
  elif [[ "${arg}" == "--imagemagick-lm" ]]; then
    ARGS="${ARGS} ${arg}"
    IM=TRUE
    IM_SCRIPT="convert-negafilm-lm.bash"
    shift
    continue
  elif [[ "${arg}" == "--imagemagick-positive" ]]; then
    ARGS="${ARGS} ${arg}"
    IM=TRUE
    IM_SCRIPT="convert-positive-color.bash"
    shift
    continue
  elif [[ "${arg}" == "--fixcaption" ]]; then
    CAPTION=TRUE
    shift
    continue
  elif [[ "${arg}" == "--"* ]]; then
    ARGS="${ARGS} ${arg}"
    PYARGS="${PYARGS} ${arg}"
    shift
    continue
  fi
  
  OUTDIR=${OUTDIR_BASE}/${PREFIX}_${DATE}
  mkdir -p ${OUTDIR}
  mkdir -p ${TMPDIR}
  filename="${arg##*/}"
  base="${filename%.*}"
  echo ${base}
  if [[ "${IM}" == "TRUE" ]]; then
    (cd ${TMPDIR} && \
      ${SCRIPT_DIR}/${IM_SCRIPT} "${arg}" "${TMPDIR}/${base}.tif")
  else
    python3 process.py ${PYARGS} --out "${TMPDIR}/${base}.tif" "${arg}"
  fi
  if [[ "${AUTOTONE}" == "TRUE" && `/usr/bin/which autotone >/dev/null 2>&1; echo $?` -eq 0 ]]; then
    autotone -n -p ${SHARPNESS} ${CONTRAST} ${WB} ${GB} ${AUTOGAMMA} -GN a -WN a "${TMPDIR}/${base}.tif" "${TMPDIR}/${base}.mpc"
    convert -define jpeg:extent=7M "${TMPDIR}/${base}.mpc" -colorspace srgb ${IM_AUTOGAMMA} ${NORMALIZE} ${MODULATE} ${COLORSPACE} "${TMPDIR}/${base}.jpg"
  else
    convert -define jpeg:extent=7M "${TMPDIR}/${base}.tif" -colorspace srgb ${IM_AUTOGAMMA} ${NORMALIZE} ${MODULATE} ${COLORSPACE} "${TMPDIR}/${base}.jpg"
  fi
  if [[ "${CAPTION}" == "TRUE" ]]; then
    exiftool -overwrite_original_in_place \
        -TagsFromFile "${arg}" "-all:all>all:all" \
        "-iptc:caption-abstract<\$iptc:caption-abstract, \$make \$model, process options: ${ARGS}" \
          "${TMPDIR}/${base}.jpg"
  else
    exiftool -overwrite_original_in_place \
        -TagsFromFile "${arg}" "-all:all>all:all" \
          "${TMPDIR}/${base}.jpg"
  fi
  mv -f "${TMPDIR}/${base}.jpg" "${OUTDIR}"
done
rm -rf ${TMPDIR}

trap "rm -rf ${TMPDIR}" 1 2 3 15
