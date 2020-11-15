#!/usr/bin/env python3

import sys
import os

#CCA_HOME = '/opt/cca'
#VAR_DIR = '/var/lib/cca'

CCA_HOME = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
VAR_DIR = os.path.join(CCA_HOME, 'var')

#

CCA_SCRIPTS_DIR = os.path.join(CCA_HOME, 'scripts')
DD_DIR = os.path.join(VAR_DIR, 'dd')
