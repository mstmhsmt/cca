#!/bin/bash

DIST_DIR=$(dirname $(dirname $0))
. ${DIST_DIR}/common.sh

if [ $# -ne 1 ]; then
    echo "usage: $(basename $0) PROJ_ID"
    exit 0
fi

PROJ_ID=$1

ORIG_DIR=${CCA_PROJECTS_DIR}/${PROJ_ID}
PATCHED_DIR=${DD_DIR}/variant/${PROJ_ID}
RES_DIR=${DD_DIR}/test_result/${PROJ_ID}

CMD=${DD_SCRIPTS_DIR}/count_tokens_in_patch.sh

echo "project: ${PROJ_ID}"

for p in $(\ls -d ${ORIG_DIR}/*g); do
    d=$(basename $p)
    vpair=${d}-${d/g/b}

    if [ ! -d ${RES_DIR}/${vpair} ]; then
        continue
    fi

    minimal=minimal2_${vpair}
    if [ ! -f ${RES_DIR}/${vpair}/${minimal}.json ]; then
        minimal=minimal1_${vpair}
    fi

    if grep -q FAIL ${RES_DIR}/${vpair}/${minimal}.json || false; then
        echo "OK: ${RES_DIR}/${vpair}/${minimal}.json"
    else
        echo "[WARNING] invalid result: ${RES_DIR}/${vpair}/${minimal}.json"
    fi
    CMD_LINE="${CMD} ${ORIG_DIR}/$d ${PATCHED_DIR}/${vpair}/${minimal}"
    echo "${CMD_LINE}"
    ${CMD_LINE}

done

echo "finished."
