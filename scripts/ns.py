#-*- coding: utf-8 -*-

'''
  Common namespaces

  Copyright 2012-2017 Codinuum Software Lab <http://codinuum.com>

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
'''


XSD_NS = 'http://www.w3.org/2001/XMLSchema#'
RDF_NS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
OWL_NS = 'http://www.w3.org/2002/07/owl#'

FB_NS = 'http://codinuum.com/fb/'

GUARD_NS = 'http://codinuum.com/fact/guard/'

SRC_NS = 'http://codinuum.com/ontologies/2012/10/source-code-entity#'
VER_NS = 'http://codinuum.com/ontologies/2012/10/versioning#'
CLONE_NS = 'http://codinuum.com/ontologies/2013/01/clone#'
CCFX_NS = 'http://codinuum.com/ontologies/2015/02/ccfx#'
SOOT_NS = 'http://codinuum.com/ontologies/2016/05/soot#'

C_NS = 'http://codinuum.com/ontologies/2012/10/c-entity#'
JAVA_NS = 'http://codinuum.com/ontologies/2012/10/java-entity#'
V_NS = 'http://codinuum.com/ontologies/2012/10/verilog-entity#'
PY_NS = 'http://codinuum.com/ontologies/2012/10/python-entity#'

GIT_NS = 'http://codinuum.com/ontologies/2014/06/git#'
SVN_NS = 'http://codinuum.com/svn/fact/predicate#'

NCC_NS = 'http://codinuum.com/ontologies/2014/06/ncc#'

ICFGC_NS = 'http://codinuum.com/ontologies/2014/08/interprocedural-control-flow-c#'

def make_guard_ns(ns):
    return GUARD_NS+'?orig='+ns


# instances

MISSING_ENT_NS = 'http://codinuum.com/fact/missing-entity/'


PREFIX_TBL = { 'xsd'   : XSD_NS,
               'rdf'   : RDF_NS,
               'owl'   : OWL_NS,
               'fb'    : FB_NS,
               'src'   : SRC_NS,
               'ver'   : VER_NS,
               'clone' : CLONE_NS,
               'ccfx'  : CCFX_NS,
               'soot'  : SOOT_NS,
               'c'     : C_NS,
               'java'  : JAVA_NS,
               'v'     : V_NS,
               'py'    : PY_NS,
               'git'   : GIT_NS,
               'ncc'   : NCC_NS,
               'icfgc' : ICFGC_NS,
               'guard' : GUARD_NS,

               'ent'      : 'http://codinuum.com/fact/entity/',
               'ext'      : 'http://codinuum.com/fact/external-name/',
               'bid'      : 'http://codinuum.com/fact/binding/',
               'rel'      : 'http://codinuum.com/fact/version/release/',
               'svnrev'   : 'http://codinuum.com/fact/version/svn/revision/',
               'gitrev'   : 'http://codinuum.com/fact/version/git/revision/',
               'variant'  : 'http://codinuum.com/fact/version/variant/',

               'missing'  : MISSING_ENT_NS,
               'gsrc'     : make_guard_ns(SRC_NS),
           }


NS_TBL = {}
for (k, v) in PREFIX_TBL.iteritems():
    NS_TBL[k+'_ns'] = v