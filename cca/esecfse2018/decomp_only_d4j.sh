#!/bin/bash

DIST_DIR=$(dirname $0)

. ${DIST_DIR}/common.sh

cmdname=$(basename $0)
function usage()
{
  echo "usage: ${cmdname} [-a dd|ddmin] [-m 8|16|32|64] [-s] [-l N] [-t R] [-u N] [-x] [-c] [-g] PROJ_ID" 1>&2
}

FB_OPTS=
DDJ_OPTS=

while getopts "a:m:sl:t:u:xcg" OPT; do
    case ${OPT} in
        a)
            DDJ_OPTS="${DDJ_OPTS} -a ${OPTARG}"
            ;;
        m)
            FB_OPTS="${FB_OPTS} --mem ${OPTARG}"
            ;;
        s)
            DDJ_OPTS="${DDJ_OPTS} --staged"
            ;;
        l)
            DDJ_OPTS="${DDJ_OPTS} --max-stmt-level ${OPTARG}"
            ;;
        t)
            DDJ_OPTS="${DDJ_OPTS} --modified-stmt-rate-thresh ${OPTARG}"
            ;;
        u)
            DDJ_OPTS="${DDJ_OPTS} --shuffle ${OPTARG}"
            ;;
        x)
            DDJ_OPTS="${DDJ_OPTS} --optout"
            ;;
        c)
            DDJ_OPTS="${DDJ_OPTS} --custom-split"
            ;;
        g)
            DDJ_OPTS="${DDJ_OPTS} --greedy"
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
#echo FB_OPTS=${FB_OPTS}
#echo DDJ_OPTS=${DDJ_OPTS}

PROJ_ID_=${PROJ_ID}_d4j

date && \
echo "* Preparing source files..." && \
${DIST_DIR}/prepare_d4j.py -p ${PROJ_ID} --projs-dir ${CCA_PROJECTS_DIR} && \
date && \
echo "* Removing .git..." && \
rm -rf ${CCA_PROJECTS_DIR}/${PROJ_ID_}/*/.git && \
date && \
echo "* Comparing source files..." && \
${DIST_DIR}/diffast.sh ${PROJ_ID_} && \
date && \
echo "* Setting up factbase..." && \
${DD_SCRIPTS_DIR}/setup_factbase.py${FB_OPTS} ${PROJ_ID_} && \
date && \
sleep 5 && \
echo "* Decomposing delta..." && \
${DD_SCRIPTS_DIR}/decompose_delta.py ${PROJ_ID_} >& ${VAR_DIR}/${PROJ_ID}.decomp.log && \
date && \
echo "* Shutting down Virtuoso..." && \
${DD_SCRIPTS_DIR}/shutdown_virtuoso.py ${PROJ_ID_} && \
date && \
echo "* Finished."

if [ -d /mnt/results ]; then
    cp -r ${VAR_DIR}/${PROJ_ID}/decomp.log /mnt/results/
fi
