#!/usr/bin/env python3

'''
  prepare_d4j.py

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
import os
import shutil
import logging

from conf import CCA_SCRIPTS_DIR

sys.path.append(CCA_SCRIPTS_DIR)

import proc
from check_d4j import get_info, get_test_dir, d4j_checkout, checkout
from siteconf import PROJECTS_DIR

logger = logging.getLogger()

D4J_CONFIG = '.defects4j.config'
D4J_PROP = 'defects4j.build.properties'

PROJ_LIST = [
    'Chart',
    'Closure',
    'Lang',
    'Math',
    'Mockito',
    'Time',
]

def get_bugs(name):
    try:
        m = __import__(name+'_d4j')
        return m.BUGS
    except Exception as e:
        logger.warning('cannot find conf for "%s": %s' % (name, str(e)))


def empty(path):
    def doit(info, bid, base_path):
        p = os.path.join(base_path, path)
        #logger.info('emptying %s...' % p)
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p)
                os.mkdir(p)
    return doit

def remove(tbl):
    def doit(info, bid, base_path):
        l = tbl.get(bid, [])
        for f in l:
            os.remove(os.path.join(base_path, f))
    return doit

def symlink(tbl):
    def doit(info, bid, base_path):
        p = tbl.get(bid, None)
        if p:
            (src, dst) = p
            os.symlink(src, os.path.join(base_path, dst))
    return doit

def patch(info, bid, dpath):
    fw_path = info['framework_path']
    patch_path_base = os.path.join(fw_path, 'patches')
    patch = os.path.join(fw_path, 'patches', '%s.test.patch' % bid)
    if os.path.exists(patch):
        cmd = 'patch -N -p1 -d %s -i %s' % (dpath, patch)
        proc.system(cmd)



EXTRA_PRE_OP_TBL = {
#     'Time' : symlink({22 : ('JodaTime/src', 'src'),
#                       24 : ('JodaTime/src', 'src'),
#                       25 : ('JodaTime/src', 'src'),
#                       26 : ('JodaTime/src', 'src'),
#                       27 : ('JodaTime/src', 'src'),
#     }),
}

EXTRA_POST_OP_TBL = {
    'Chart' : empty('experimental'),
    'Mockito' : remove({15 : ['test/org/mockito/internal/util/reflection/BeanPropertySetterTest.java'],
                        16 : ['test/org/mockito/internal/MockitoCoreTest.java'],
                        17 : ['test/org/mockito/internal/util/ArrayUtilsTest.java'],
                        25 : ['test/org/mockito/internal/util/reflection/GenericMetadataSupportTest.java'],
    }),
}

def prepare(dpath, proj_id=None):

    if not os.path.exists(dpath):
        os.makedirs(dpath)

    for proj in PROJ_LIST:
        if proj_id:
            if proj != proj_id:
                continue

        bugs = get_bugs(proj)

        proj_path = os.path.join(dpath, proj+'_d4j')

        proj_info = get_info(proj)

        vcs = proj_info['vcs']
        repo = proj_info['repo']
        commit_db = proj_info['commit_db']

        for bid in bugs:
            (prev, rev) = commit_db[str(bid)]

            pver = '%sp' % bid
            bver = '%sb' % bid
            fver = '%sf' % bid

            ppath = os.path.join(proj_path, pver)
            bpath = os.path.join(proj_path, bver)
            fpath = os.path.join(proj_path, fver)

            if os.path.exists(ppath):
                logger.warning('already exists, skipping...')
                continue

            checkout(vcs, repo, prev, ppath)
            d4j_checkout(proj, bver, bpath)
            d4j_checkout(proj, fver, fpath)

            if proj == 'Chart' and bid == 19:
                x = os.path.join('lib', 'itext-2.0.6.jar')
                os.remove(os.path.join(ppath, x))
                os.remove(os.path.join(fpath, x))

            op = EXTRA_PRE_OP_TBL.get(proj, None)
            if op:
                op(proj_info, bid, ppath)

            shutil.copy2(os.path.join(bpath, D4J_CONFIG),
                         os.path.join(ppath, D4J_CONFIG))

            shutil.copy2(os.path.join(bpath, D4J_PROP),
                         os.path.join(ppath, D4J_PROP))

            test_dir_name = get_test_dir(bpath)
            p_test_dir = os.path.join(ppath, test_dir_name)
            b_test_dir = os.path.join(bpath, test_dir_name)

            if os.path.exists(p_test_dir):
                shutil.rmtree(p_test_dir)
                shutil.move(b_test_dir, p_test_dir)

            for x in os.listdir(bpath):
                b = os.path.join(bpath, x)
                if os.path.isfile(b):
                    p = os.path.join(ppath, x)
                    if not os.path.exists(p):
                        shutil.copy2(b, p)

            #shutil.rmtree(bpath)

            op = EXTRA_POST_OP_TBL.get(proj, None)
            if op:
                op(proj_info, bid, ppath)



if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='check Defects4J repository',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--projs-dir', dest='projs_dir', type=str, default=PROJECTS_DIR,
                        help='destination directory')

    parser.add_argument('-p', '--proj', dest='proj', type=str, default=None,
                        choices=PROJ_LIST, help='project ID')

    args = parser.parse_args()

    prepare(args.projs_dir, proj_id=args.proj)
