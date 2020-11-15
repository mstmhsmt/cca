#!/bin/bash

. $(dirname $0)/common.sh

if [ $# -lt 1 ]; then
    echo usage: $0 PROJ_ID [OPTS]
    exit 0
fi

PROJ_ID=$1

shift

${DD_SCRIPTS_DIR}/ddjava.py -v -k --src ${CCA_PROJECTS_DIR}/${PROJ_ID} \
--script ${DIST_DIR}/d4j ${DD_DIR} ${PROJ_ID} $* >& ${DD_DIR}/${PROJ_ID}.log
