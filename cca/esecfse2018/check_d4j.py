#!/usr/bin/env python3

'''
  check_d4j.py

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
import re
import tempfile
import shutil
import csv
import logging

from conf import CCA_SCRIPTS_DIR

sys.path.append(CCA_SCRIPTS_DIR)

import proc
import SVN

logger = logging.getLogger()


PATCH_PAT = re.compile(r'^(?P<id>[0-9]+)\.src\.patch$')
VCS_PAT = re.compile(r'^Vcs: Vcs::(?P<vcs>[a-zA-z]+)$')
REPO_PAT = re.compile(r'^Repository: (?P<path>[a-zA-z0-9/_.:-]+)$')
REV_PAT = 'Revision ID (fixed version):'
NBUGS_PAT = re.compile(r'Number of bugs: (?P<n>[0-9]+)')
COMMIT_DB_PAT = re.compile(r'^Commit db: (?P<path>[a-zA-z0-9/_.:-]+)$')

INFO_CMD_FMT = 'defects4j info -p {proj}'
D4J_CHECKOUT_CMD_FMT = 'defects4j checkout -p {proj} -v {ver} -w {wdir}'
GET_TEST_DIR_CMD_FMT = 'defects4j export -p dir.src.tests -w {wdir}'

GIT_CHECKOUT_CMD_FMT = 'git archive --format=tar {rev} | tar x -C {wdir}'
FILT_CMD_FMT = "find {dpath} -type f -and -not -regex '.*\.java' -delete"
DIFF_CMD_FMT = 'diff -u -r -b -w -B -E {old} {new}'
FMT_CMD_FMT = 'astyle --style=java --delete-empty-lines --indent=spaces {path}'

COMMENT_PAT = re.compile(r'/\*([^*]|\*[^/])*\*/|//.*\n')

def read_commit_db(path):
    tbl = {}
    with open(path) as f:
        for row in csv.reader(f):
            bid = row[0]
            prev = row[1]
            rev = row[2]
            tbl[bid] = (prev, rev)

    return tbl
        

def get_info(proj):
    cmd = INFO_CMD_FMT.format(proj=proj)
    lines = None
    with proc.PopenContext(cmd) as p:
        (lines, e) = p.communicate()

    vcs = None
    repo = None
    commit_db = None
    framework_path = None
    nbugs = None

    for _line in lines.split(os.linesep):
        line = _line.strip()

        m = VCS_PAT.match(line)
        if m:
            vcs = m.group('vcs')

        m = REPO_PAT.match(line)
        if m:
            repo = m.group('path')

        m = COMMIT_DB_PAT.match(line)
        if m:
            commit_db_path = m.group('path')
            commit_db = read_commit_db(commit_db_path)
            framework_path = os.path.dirname(commit_db_path)

        m = NBUGS_PAT.match(line)
        if m:
            nbugs = int(m.group('n'))

        if vcs and repo and commit_db and nbugs:
            break

    return {'vcs':vcs,
            'repo':repo,
            'commit_db':commit_db,
            'framework_path':framework_path,
            'nbugs':nbugs}


def d4j_checkout(proj, ver, wdir):
    logger.info('{} --> {}'.format(ver, wdir))
    cmd = D4J_CHECKOUT_CMD_FMT.format(proj=proj,ver=ver,wdir=wdir)
    rc = proc.system(cmd, quiet=True)
    return rc

def git_checkout(repo, rev, wdir):
    logger.info('{} --> {}'.format(rev, wdir))

    wdir = os.path.abspath(wdir)

    if not os.path.exists(wdir):
        os.makedirs(wdir)

    cmd = GIT_CHECKOUT_CMD_FMT.format(rev=rev,wdir=wdir)

    rc = proc.system(cmd, cwd=repo)

    return rc

def svn_checkout(repo, rev, wdir):
    logger.info('{} --> {}'.format(rev, wdir))
    r = SVN.Repository(repo)
    r.checkout(wdir, rev)

def checkout(vcs, repo, rev, wdir):
    if vcs == 'Git':
        git_checkout(repo, rev, wdir)
    elif vcs == 'Svn':
        svn_checkout(repo, rev, wdir)

def cleanup_dir(dir_path):
    for (dpath, dns, fns) in os.walk(dir_path, topdown=False):
        if len(os.listdir(dpath)) == 0:
            os.rmdir(dpath)

def filter_dir(dpath):
    cmd = FILT_CMD_FMT.format(dpath=dpath)
    rc = proc.system(cmd)
    return rc

def get_test_dir(wdir):
    cmd = GET_TEST_DIR_CMD_FMT.format(wdir=wdir)
    d = None
    with proc.PopenContext(cmd) as p:
        (d, e) = p.communicate()

    return d

def diff(d1, d2):
    cmd = DIFF_CMD_FMT.format(old=d1,new=d2)
    d = None
    with proc.PopenContext(cmd, rc_check=False) as p:
        (d, e) = p.communicate()

    return d

def format_src1(fpath):
    orig = None
    content = None

    with open(fpath, 'r') as f:
        orig = f.read()
        content = COMMENT_PAT.sub('', orig)

    if orig != content:
        with open(fpath, 'w') as f:
            f.write(content)

    cmd = FMT_CMD_FMT.format(path=fpath)

    rc = proc.system(cmd, quiet=True)

    orig_path = fpath+'.orig'

    if os.path.exists(orig_path):
        os.remove(orig_path)

    return rc

def format_src(dir_path):
    for (dpath, dns, fns) in os.walk(dir_path):
        for fn in fns:
            if fn.endswith('.java'):
                path = os.path.join(dpath, fn)
                format_src1(path)


def check(proj, wdir=None):
    info = get_info(proj)

    vcs = info['vcs']
    repo = info['repo']
    commit_db = info['commit_db']
    nbugs = info['nbugs']

    remove_wdir = False

    if wdir:
        temp_dir = os.path.abspath(wdir)
    else:
        remove_wdir = True
        temp_dir = tempfile.mkdtemp('', 'd4j_{}_'.format(proj))

    logger.info('{}:{}:{}'.format(vcs, repo, nbugs))

    l = []

    for bid in range(1, nbugs + 1):

        (prev, rev) = commit_db[str(bid)]

        logger.info('*** {}: {}--{}'.format(bid, prev, rev))

        vprev = '{}p'.format(bid)
        vbug = '{}b'.format(bid)

        vprev_dir = os.path.join(temp_dir, vprev)
        vbug_dir = os.path.join(temp_dir, vbug)

        logger.info('checking out sources...')
        checkout(vcs, repo, prev, vprev_dir)
        d4j_checkout(proj, vbug, vbug_dir)

        logger.info('removing test code...')
        test_dir = get_test_dir(vbug_dir)
        prev_test_dir = os.path.join(vprev_dir, test_dir)
        if os.path.exists(prev_test_dir):
            shutil.rmtree(prev_test_dir)
        shutil.rmtree(os.path.join(vbug_dir, test_dir))

        logger.info('filtering out irrelevant files...')
        filter_dir(vprev_dir)
        cleanup_dir(vprev_dir)
        filter_dir(vbug_dir)
        cleanup_dir(vbug_dir)

        logger.info('formatting source files...')
        format_src(vprev_dir)
        format_src(vbug_dir)

        logger.info('comparing source files...')
        delta = diff(vprev_dir, vbug_dir)

        if delta and delta.find('.java') >= 0:
            logger.info('DELTA: {} -- {}'.format(prev, vbug))
            print(delta)
            l.append((bid, prev, rev))

    if remove_wdir:
        logger.info('removing "{}"...'.format(temp_dir))
        shutil.rmtree(temp_dir)

    if l:
        bugs = []
        logger.info('CANDIDATES ({}):'.format(len(l)))
        for (bid, prev, rev) in l:
            bugs.append(bid)
            logger.info('{}: {}:{}'.format(bid, prev, rev))

        print(bugs)


if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='check Defects4J repository',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-w', '--work-dir', dest='wdir', default=None,
                        help='use working directory', metavar='PATH')

    parser.add_argument('proj', type=str, help='project id')

    args = parser.parse_args()

    check(args.proj, wdir=args.wdir)
