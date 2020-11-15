#!/bin/bash

DIST_DIR=$(dirname $(dirname $0))
. ${DIST_DIR}/common.sh

if [ $# -ne 1 ]; then
    echo "usage: $(basename $0) PROJ_ID"
    exit 0
fi

PROJ_ID=$1

ORIG_DIR=${UNPARSED_PROJECTS_DIR}/${PROJ_ID}
PATCHED_DIR=${DD_DIR}/variant/${PROJ_ID}
RES_DIR=${DD_DIR}/test_result/${PROJ_ID}
OUT_DIR=${DD_DIR}/patches/${PROJ_ID}

if [ ! -d ${OUT_DIR} ]; then
    mkdir -p ${OUT_DIR}
fi

if [ ! -d ${UNPARSED_PROJECTS_DIR} ]; then
    mkdir -p ${UNPARSED_PROJECTS_DIR}
fi

if [ ! -d ${ORIG_DIR} ]; then
    cp -r ${CCA_PROJECTS_DIR}/${PROJ_ID} ${UNPARSED_PROJECTS_DIR}/
fi

CMD=${DD_SCRIPTS_DIR}/make_text_patch.sh

echo "project: ${PROJ_ID}"

for p in $(\ls -d ${ORIG_DIR}/*g); do
    d=$(basename $p)
    vpair=${d}-${d/g/b}

    if [ ! -d ${RES_DIR}/${vpair} ]; then
        continue
    fi

    fail_or_minimal=minimal

    if ls ${RES_DIR}/${vpair}/fail* 2>/dev/null || false; then
        fail_or_minimal=fail
    fi

    prefixes=
    for f in $(\ls ${RES_DIR}/${vpair}/*${fail_or_minimal}*.json); do
        x=$(basename $f)
        if [ ${fail_or_minimal} = 'fail' ]; then
            p=${x%fail*}
        else
            p=${x%minimal*}
        fi
        prefixes="${prefixes} ${p}"
    done

    for prefix in "" ${prefixes}; do
        echo "prefix: ${prefix}"

        _fail_or_minimal=${prefix}${fail_or_minimal}

        stgs=
        for f in $(\ls ${RES_DIR}/${vpair}/${_fail_or_minimal}*.json); do
            x=$(basename $f)
            if [ ${fail_or_minimal} = 'fail' ]; then
                y=${x#*fail}
            else
                y=${x#*minimal}
            fi
            stgs="${stgs} ${y%_*-*.json}"
        done

        for stg in ${stgs}; do
            fail=${prefix}fail${stg}_${vpair}
            minimal=${prefix}minimal${stg}_${vpair}
            patch=${PROJ_ID}_${prefix}${stg}_${vpair}.diff

            if grep -q FAIL ${RES_DIR}/${vpair}/${minimal}.json || false; then
                fail=${minimal}
                echo "OK: ${RES_DIR}/${vpair}/${fail}.json"

            elif grep -q FAIL ${RES_DIR}/${vpair}/${fail}.json || false; then
                echo "OK: ${RES_DIR}/${vpair}/${fail}.json"
            else
                echo "[WARNING] invalid result: ${RES_DIR}/${vpair}/${fail}.json"
            fi
            CMD_LINE="${CMD} ${ORIG_DIR}/$d ${PATCHED_DIR}/${vpair}/${fail} ${OUT_DIR}/${patch}"
            echo "${CMD_LINE}"
            ${CMD_LINE}
        done

    done

done

echo "finished."
