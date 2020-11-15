#!/bin/bash

DIST_DIR=$(dirname $(dirname $0))
. ${DIST_DIR}/common.sh

if [ $# -ne 1 ]; then
    echo "usage: $(basename $0) PROJ_ID"
    exit 0
fi

PROJ_ID=$1

PROJ_DIR=${CCA_PROJECTS_DIR}/${PROJ_ID}
DEST_DIR=${UNPARSED_PROJECTS_DIR}/${PROJ_ID}

if [ ! -d ${DEST_DIR} ]; then
    mkdir -p ${DEST_DIR}
fi

for d in $(\ls -d ${PROJ_DIR}/*g); do
    ${DD_SCRIPTS_DIR}/make_unparsed_copy.py $d ${DEST_DIR}/$(basename $d)
done
