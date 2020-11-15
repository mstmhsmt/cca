#!/bin/bash

DIST_DIR=$(dirname $0)

. ${DIST_DIR}/common.sh

cmdname=$(basename $0)
function usage()
{
  echo "usage: ${cmdname} [-a dd|ddmin] [-d] [-s] [-u N] [-g] PROJ_ID" 1>&2
}

DDP_OPTS=

while getopts "a:dsu:g" OPT; do
    case ${OPT} in
        a)
            DDP_OPTS="${DDP_OPTS} -a ${OPTARG}"
            ;;
        d)
            DDP_OPTS="${DDP_OPTS} --debug"
            ;;
        s)
            DDP_OPTS="${DDP_OPTS} --staged"
            ;;
        u)
            DDP_OPTS="${DDP_OPTS} --shuffle ${OPTARG}"
            ;;
        g)
            DDP_OPTS="${DDP_OPTS} --greedy"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

shift $((OPTIND - 1))

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

PROJ_ID="$1"

#echo PROJ_ID=${PROJ_ID}
#echo DDP_OPTS=${DDP_OPTS}

PROJ_ID_=${PROJ_ID}_d4j

date && \
echo "* Preparing source files..." && \
${DIST_DIR}/prepare_d4j.py -p ${PROJ_ID} --projs-dir ${CCA_PROJECTS_DIR} && \
date && \
echo "* Removing .git..." && \
rm -rf ${CCA_PROJECTS_DIR}/${PROJ_ID_}/*/.git && \
date && \
echo "* Performing DD..." && \
${DIST_DIR}/ddp_d4j.sh ${PROJ_ID_}${DDP_OPTS} && \
date && \
echo "* Checking text patches..." && \
${DIST_DIR}/check_patches.py -o ${VAR_DIR}/dd/${PROJ_ID_}.check.csv ${PROJ_ID_} && \
date && \
echo "* Finished."

if [ -d /mnt/results/ ]; then
    cp -r ${VAR_DIR}/dd/* /mnt/results/
fi
