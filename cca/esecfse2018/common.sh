#!/bin/bash

#CCA_HOME=/opt/cca
#DIST_DIR=${CCA_HOME}/esecfse2018
#VAR_DIR=/var/lib/cca
#EXAMPLES_DIR=${HOME}/regression_examples

DIST_DIR=${DIST_DIR:-$(dirname $0)}
CCA_HOME=$(dirname ${DIST_DIR})
VAR_DIR=${CCA_HOME}/var
EXAMPLES_DIR=${CCA_HOME}/regression_examples

CCA_SCRIPTS_DIR=${CCA_HOME}/scripts
DD_SCRIPTS_DIR=${CCA_HOME}/ddutil
DB_DIR=${VAR_DIR}/db
DD_DIR=${VAR_DIR}/dd
CCA_PROJECTS_DIR=${VAR_DIR}/projects
UNPARSED_PROJECTS_DIR=${VAR_DIR}/unparsed-projects
