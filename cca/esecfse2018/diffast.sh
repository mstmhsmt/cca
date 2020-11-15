#!/bin/bash

DIST_DIR=$(dirname $0)

. ${DIST_DIR}/common.sh


if [ $# -ne 1 ]; then
    echo "usage: $0 PROJ_ID"
    exit 0
fi

PROJ_ID=$1

BASE_DIR=${VAR_DIR}/work

if [ ! -d ${BASE_DIR} ]; then
    mkdir -p ${BASE_DIR}
fi

echo PROJ_ID=\"${PROJ_ID}\"

OS=$(uname -s)

TIME=time
CORE_COUNT=1

if [ ${OS} = 'Linux' ]; then
    TIME=/usr/bin/time
    CORE_COUNT=$(grep 'core id' /proc/cpuinfo | sort | uniq | wc -l)
elif [ ${OS} = 'Darwin' ]; then
    TIME=/opt/local/bin/gtime
    CORE_COUNT=$(sysctl -n machdep.cpu.core_count)
fi

echo CORE_COUNT=${CORE_COUNT}

NPROCS_OPT="-p $CORE_COUNT"

OUTDIR=$VAR_DIR/fact/${PROJ_ID}

FACTSIZE_THRESH=100000

ENC=FDLCO

${TIME} -o ${BASE_DIR}/time.build_factbase.diffts-${PROJ_ID} \
/usr/bin/env CCA_PROJECTS_DIR=${CCA_PROJECTS_DIR} \
${CCA_SCRIPTS_DIR}/cca_command.py ${NPROCS_OPT} -b ${BASE_DIR} \
diff_versions_for_fact -a \
" --keep-going --sim --sim-thresh 0.8 --mapping --changes --ast --dump-delta --delta --into-directory ${OUTDIR} --encoding ${ENC} --fact-size-thresh ${FACTSIZE_THRESH}" ${PROJ_ID}
