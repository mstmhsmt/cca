#!/bin/bash

. $(dirname $0)/common.sh

if [ $# -lt 1 ]; then
    echo usage: $0 PROJ_ID [OPTS]
    exit 0
fi

PROJ_ID=$1

if [ ! -d ${DD_DIR} ]; then
    mkdir -p ${DD_DIR}
fi

shift

/usr/bin/env CCA_PROJECTS_DIR=${CCA_PROJECTS_DIR} \
${DD_SCRIPTS_DIR}/ddplain.py -v -k --src ${CCA_PROJECTS_DIR}/${PROJ_ID} \
--script ${DIST_DIR}/d4j ${DD_DIR} ${PROJ_ID} $* >& ${DD_DIR}/${PROJ_ID}.log
