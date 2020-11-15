#!/usr/bin/env python3

'''
  info.py

  Copyright 2018-2020 Chiba Institute of Technology

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

__author__ = 'Masatomo Hashimoto <m.hashimoto@stair.center>'

import sys

from conf import CCA_SCRIPTS_DIR

sys.path.append(CCA_SCRIPTS_DIR)

import project


def get_parts_d4j(proj_id):
    parts = []
    try:
        m = __import__(proj_id)
        parts  = m._BUGS
    except:
        pass
    return parts

def get_examples_d4j(proj_id):
    bugs = []
    try:
        m = __import__(proj_id)
        bugs  = m.BUGS
    except:
        pass
    return bugs

def get_examples_ddj(proj_id):
    l = []
    try:
        m = __import__(proj_id)
        l  = m.EXAMPLES
    except:
        pass
    return l

def get_list(proj_id):
    l = []
    if proj_id.endswith('_d4j'):
        l = get_parts_d4j(proj_id)
    elif proj_id.endswith('_ddj'):
        l = get_examples_ddj(proj_id)
    return l

def get_examples(proj_id):
    l = []
    if proj_id.endswith('_d4j'):
        l = get_examples_d4j(proj_id)
    elif proj_id.endswith('_ddj'):
        l = get_examples_ddj(proj_id)
    return l

def get_nparts_d4j(proj_id):
    return len(get_parts_d4j(proj_id))

def get_nparts_ddj(proj_id):
    return 1

def get_nparts(proj_id):
    n = 0
    if proj_id.endswith('_d4j'):
        n = get_nparts_d4j(proj_id)
    elif proj_id.endswith('_ddj'):
        n = get_nparts_ddj(proj_id)
    return n

if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='project info',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('projs', metavar='PROJ_ID', type=str, nargs='*', help="project ID(s)")

    parser.add_argument('--nparts', dest='nparts', action='store_true',
                        help='only show the number of parts')

    args = parser.parse_args()

    confs = project.get_confs()

    if args.projs == []:

        print('%d projects found:' % len(confs))

        d4j_projects = []
        ddj_projects = []

        max_len = 0

        for mname in confs:
            conf = project.get_conf(mname)
            if conf:
                n = len(conf.proj_id)
                if n > max_len:
                    max_len = n

                if mname.endswith('_d4j'):
                    d4j_projects.append(conf)
                else:
                    ddj_projects.append(conf)

        fmt = '  %%-%ds (%%d examples)%%s' % max_len

        print('projects from Defects4J:')
        for conf in d4j_projects:
            nparts_str = ''
            nparts = get_nparts_d4j(conf.proj_id)
            if nparts:
                nparts_str = ' (%d parts)' % nparts

            print(fmt % (conf.proj_id, len(conf.vpairs), nparts_str))

        print('')

        nparts = ''
        print('other projects:')
        for conf in ddj_projects:
            print(fmt % (conf.proj_id, len(conf.vpairs), nparts))

    else:
        projs = project.get_confs()
        for proj_id in args.projs:
            if proj_id in projs:
                if args.nparts:
                    print('%d' % get_nparts(proj_id))
                else:
                    l = get_list(proj_id)
                    el = get_examples(proj_id)
                    print('%s (%d examples):' % (proj_id, len(el)))
                    print(', '.join([str(x) for x in l]))
                    print('')
            else:
                print('no such project: "%s"' % proj_id)
