#!/usr/bin/env python3

import sys
import os

#CCA_HOME = '/opt/cca'
#VAR_DIR = '/home/ddj/data'

CCA_HOME = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
VAR_DIR = os.path.join(CCA_HOME, 'var')

VIRTUOSO_PW = 'ddj'
VIRTUOSO_PORT = 1111

DEPENDENCIES_INSTALLER = 'install_dependencies.sh'

#

CCA_SCRIPTS_DIR = os.path.join(CCA_HOME, 'scripts')
CCA_ONT_DIR     = os.path.join(CCA_HOME, 'ontologies')
FACTUTILS_DIR   = os.path.join(CCA_HOME, 'factutils')

FB_DIR     = os.path.join(VAR_DIR, 'db')
FACT_DIR   = os.path.join(VAR_DIR, 'fact')
WORK_DIR   = os.path.join(VAR_DIR, 'work')
REFACT_DIR = os.path.join(VAR_DIR, 'refactoring')
DD_DIR     = os.path.join(VAR_DIR, 'dd')
LOG_DIR    = os.path.join(VAR_DIR, 'log')
