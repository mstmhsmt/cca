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

PROJ_ID_=${PROJ_ID}_ddj

date
echo "* Preparing source files..."
if [ ! -d ${CCA_PROJECTS_DIR}/${PROJ_ID_} ]; then
    mkdir -p ${CCA_PROJECTS_DIR}
    tar -C ${CCA_PROJECTS_DIR} -Jxf ${EXAMPLES_DIR}/${PROJ_ID_}.txz &> /dev/null
    INSTALLER=${CCA_PROJECTS_DIR}/${PROJ_ID_}/install_dependencies.sh
    if [ -f ${INSTALLER} ]; then
        ${INSTALLER}
    fi
fi

date && \
echo "* Performing DD..." && \
${DIST_DIR}/ddp_ddj.sh ${PROJ_ID_}${DDP_OPTS} && \
echo "* Performing token diff..." && \
${DIST_DIR}/ddj/count_tokens_in_patch_for_proj.sh ${PROJ_ID_} && \
date && \
echo "* Finished."

if [ -d /mnt/results/ ]; then
    cp -r ${VAR_DIR}/DD/* /mnt/results/
fi
