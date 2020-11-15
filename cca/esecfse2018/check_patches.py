#!/usr/bin/env python3

'''
  check_patches.py

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
from filecmp import dircmp
import filecmp
import re
import csv
import difflib
import logging

from conf import VAR_DIR, DD_DIR

import overlap

logger = logging.getLogger()

IGNORED = ['.git', '.svn', '.defects4j.config']

PROJECTS_DIR = os.path.join(VAR_DIR, 'projects')
VARIANT_DIR = os.path.join(DD_DIR, 'variant')

UNPARSED_PROJECTS_DIR = os.path.join(VAR_DIR, 'unparsed-projects')


def tbl_get(tbl, key):
    try:
        l = tbl[key]
    except KeyError:
        l = []
        tbl[key] = l
    return l

def is_src(name):
    return name.endswith('.java')

def _norm_dcmp(data, odir, ndir, dcmp):
    removed = tbl_get(data, 'removed')
    added = tbl_get(data, 'added')
    modified = tbl_get(data, 'modified')

    for name in dcmp.left_only:
        if is_src(name):
            path = os.path.join(os.path.relpath(dcmp.left, odir), name)
            removed.append(path)

    for name in dcmp.diff_files:
        if is_src(name):
            lpath = os.path.join(os.path.relpath(dcmp.left, odir), name)
            rpath = os.path.join(os.path.relpath(dcmp.right, ndir), name)
            modified.append((lpath, rpath))

    for name in dcmp.right_only:
        if is_src(name):
            path = os.path.join(os.path.relpath(dcmp.right, ndir), name)
            added.append(path)

    for sub_dcmp in dcmp.subdirs.values():
        _norm_dcmp(data, odir, ndir, sub_dcmp)

def norm_dcmp(dcmp, odir, ndir):
    data = {}
    _norm_dcmp(data, odir, ndir, dcmp)
    return data

def print_norm_dcmp(d):
    for f in d['removed']:
        print('D %s' % f)

    for f in d['added']:
        print('A %s' % f)

    for p in d['modified']:
        print('M %s - %s' % p)

def lines_of_norm_dcmp(d):
    c = 0
    c += len(d['removed'])
    c += len(d['added'])
    c += len(d['modified'])
    return c

def lines_of_file(path):
    i = 0
    with open(path, 'r') as f:
        for i, _ in enumerate(f, 1):
            pass
    return i

def get_bids(proj_id):
    l = []
    for f in os.listdir(os.path.join(PROJECTS_DIR, proj_id)):
        if f.endswith('f'):
            bid = int(f.rstrip('f'))
            l.append(bid)
    l.sort()
    return l


def get_prefixes(proj_id, vp):
    d = os.path.join(VARIANT_DIR, proj_id, vp)
    PAT = re.compile(r'^a([0-9]+)-minimal([0-9]+)_%s' % vp)
    l = []
    for f in os.listdir(d):
        m = PAT.match(f)
        if m:
            try:
                n = int(m.group(1))
                l.append(n)
            except:
                pass
    pl = ['a%d-' % n for n in l]
    return pl

def get_patched(proj_id, vp, prefix=''):
    d = os.path.join(VARIANT_DIR, proj_id, vp)
    STG_PAT = re.compile(r'%sminimal([0-9]+)_%s' % (prefix, vp))
    l = []
    for f in os.listdir(d):
        m = STG_PAT.match(f)
        if m:
            try:
                i = int(m.group(1))
                l.append(i)
            except:
                pass
    if l:
        m = max(l)
        fn = '%sminimal%d_%s' % (prefix, m, vp)
    else:
        fn = '%sminimal_%s' % (prefix, vp)
    patched = os.path.join(d, fn)
    return patched

def unified_diff(path1, path2, rpath1, rpath2, n=3):
    print('comparing %s with %s' % (path1, path2))
    diff = None
    try:
        with open(path1) as f1:
            with open(path2) as f2:
                lines1 = f1.readlines()
                lines2 = f2.readlines()
                diff = difflib.unified_diff(lines1, lines2, rpath1, rpath2, n=n)

    except Exception as e:
        logger.warning(str(e))

    diff_str = ''
    if diff:
        diff_str = '\n'.join([line.strip() for line in diff])

    return diff_str

def check(proj_id, bid):
    orig = os.path.join(PROJECTS_DIR, proj_id, '%df' % bid)
    unparsed_orig = os.path.join(UNPARSED_PROJECTS_DIR, proj_id, '%df' % bid)
    bug = os.path.join(PROJECTS_DIR, proj_id, '%db' % bid)

    vp = '%(bid)df-%(bid)dp' % {'bid':bid}
    #patched = os.path.join(VARIANT_DIR, proj_id, vp, 'minimal_'+vp)

    patched_list = [get_patched(proj_id, vp, prefix='')]
    for p in get_prefixes(proj_id, vp):
        patched_list.append(get_patched(proj_id, vp, prefix=p))

    print('comparing "%s" with "%s"...' % (orig, bug))

    try:
        dcmp = dircmp(orig, bug, ignore=IGNORED)

        d4j_d = norm_dcmp(dcmp, orig, bug)

        print_norm_dcmp(d4j_d)

        dl = []

        for patched in patched_list:

            print('comparing "%s" with "%s"...' % (orig, patched))
            dcmp = dircmp(orig, patched, ignore=IGNORED)

            ddj_d = norm_dcmp(dcmp, orig, patched)

            print_norm_dcmp(ddj_d)

            same_d = d4j_d == ddj_d

            print('same_d=%s' % same_d)

            diff_d = 0 # num of files
            if not same_d:
                diff_d = lines_of_norm_dcmp(ddj_d) - lines_of_norm_dcmp(d4j_d)

            print('diff_d=%d' % diff_d)

            same_f = True
            diff_f = 0 # num of tokens
            d4j_f = 0 # num of tokens
            ddj_f = 0 # num of tokens
            overlap_f = 0 # num of tokens
            file_tbl = {}
            for (rpath0, rpath1) in d4j_d.get('modified', []):
                base = os.path.join(orig, rpath0)
                f = os.path.join(bug, rpath1)
                file_tbl[base] = (f, rpath1, rpath0)

            d4j_diff_l = []
            ddj_diff_l = []

            ddj_base_set = set()

            for (rpath0, rpath1) in ddj_d.get('modified', []):
                base = os.path.join(orig, rpath0)
                unparsed_base = os.path.join(unparsed_orig, rpath0)
                f_patched = os.path.join(patched, rpath1)

                ddj_base_set.add(base)

                try:
                    f_bug, rp, _ = file_tbl.get(base, (None, None, None))
                    info = overlap.get_overlap_info(base, f_bug, f_patched, quiet=False)
                    same_f = same_f and info['same']
                    ddj0_f = info['right']
                    d4j0_f = info['left']
                    diff_f +=  ddj0_f - d4j0_f
                    ddj_f += ddj0_f
                    d4j_f += d4j0_f
                    overlap_f += info['overlap']

                    diff1 = info['diff1']
                    diff2 = info['diff2']

                    if diff1:
                        #d4j_diff_l.append('*** %s\n' % base)
                        #d4j_diff_l.append(diff1)
                        d4j_diff_l.append(unified_diff(base, f_bug, rpath0, rp, n=3))

                    if diff2:
                        b = base
                        if os.path.exists(unparsed_base):
                            b = unparsed_base

                        #ddj_diff_l.append('*** %s\n' % base)
                        #ddj_diff_l.append(diff2)
                        ddj_diff_l.append(unified_diff(b, f_patched, rpath0, rpath1, n=3))

                except KeyError as e:
                    logger.warning(str(e))

            d4j_base_set = set(file_tbl.keys()) - ddj_base_set
            for base in d4j_base_set:
                f_bug, rp, rpath0 = file_tbl[base]
                info = overlap.get_overlap_info(base, f_bug, None, quiet=False)
                d4j0_f = info['left']
                diff_f += - d4j0_f
                d4j_f += d4j0_f
                d4j_diff_l.append(unified_diff(base, f_bug, rpath0, rp, n=3))

            d = {
                'd_same'    : same_d,
                'd_diff'    : diff_d,
                'f_same'    : same_f,
                'f_diff'    : diff_f,
                'f_d4j'     : d4j_f,
                'f_ddj'     : ddj_f,
                'f_overlap' : overlap_f,
                'diff_d4j'  : ''.join(d4j_diff_l),
                'diff_ddj'  : ''.join(ddj_diff_l),
            }

            dl.append(d)

        return dl

    except Exception as e:
        logger.warning(str(e))
        return None

def main_plain(proj_id, bid, outfile=None):
    result_tbl = {}

    if bid == None:
        bidl = get_bids(proj_id)
    else:
        bidl = [bid]

    for bid in bidl:
        try:
            result_tbl[bid] = check(proj_id, bid)
        except Exception as e:
            logger.warning(str(e))

    out = sys.stdout
    if outfile:
        out = open(outfile, 'w')

    out.write('---------- %s ----------\n' % proj_id)
    out.write('bid -> dir patch diff (num. files), file patch diff (num. tokens)\n')

    for bid in sorted(result_tbl.keys()):
        for result in result_tbl[bid]:
            if result == None:
                out.write('%d -> FAILED\n' % bid)
            else:
                same_d    = result['d_same']
                diff_d    = result['d_diff']
                same_f    = result['f_same']
                diff_f    = result['f_diff']
                d4j_f     = result['f_d4j']
                ddj_f     = result['f_ddj']
                overlap_f = result['f_overlap']

                d = '?'
                if same_d:
                    d = '='
                else:
                    if diff_d == 0:
                        d = '0'
                    else:
                        d = '%+d' % diff_d

                f = '?'
                if same_f:
                    f = '= (%d)' % d4j_f
                else:
                    if diff_f == 0:
                        f = '0'
                    else:
                        f = '%+d' % diff_f

                    f = '%s (d4j=%d,ddj=%d,overlap=%d)' % (f, d4j_f, ddj_f, overlap_f)

                out.write('%d -> %s, %s\n' % (bid, d, f))

    if out != sys.stdout:
        out.close()

def main_csv(proj_id, bid, outfile):
    result_tbl = {}

    if bid == None:
        bidl = get_bids(proj_id)
    else:
        bidl = [bid]

    for bid in bidl:
        try:
            result_tbl[bid] = check(proj_id, bid)
        except Exception as e:
            logger.warning(str(e))

    with open(outfile, 'w') as f:

        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

        hd = [
            'proj_id',
            'bid',
            'dir_diff', 'file_diff',
            'tokens_d4j', 'tokens_ddj', 'overlap',
            'diff_d4j', 'diff_ddj'
        ]

        w.writerow(hd)

        for bid in sorted(list(result_tbl.keys())):
            for result in result_tbl[bid]:
                if result == None:
                    w.writerow([proj_id, str(bid), '?', '?', '?', '?', '?', '?', '?'])
                else:
                    same_d    = result['d_same']
                    diff_d    = result['d_diff']
                    same_f    = result['f_same']
                    diff_f    = result['f_diff']
                    d4j_f     = result['f_d4j']
                    ddj_f     = result['f_ddj']
                    overlap_f = result['f_overlap']

                    diff_d4j = result['diff_d4j']
                    diff_ddj = result['diff_ddj']

                    d = '?'
                    if same_d:
                        d = '0'
                    else:
                        if diff_d == 0:
                            d = '0'
                        else:
                            d = '%+d' % diff_d

                    f = '?'
                    if same_f:
                        f = '0'
                    else:
                        if diff_f == 0:
                            f = '0'
                        else:
                            f = '%+d' % diff_f

                    row = [ proj_id, str(bid), d, f, str(d4j_f), str(ddj_f), str(overlap_f),
                            diff_d4j, diff_ddj ]

                    w.writerow(row)


if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='check generated patches against Defects4J patches',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('proj_id', type=str, help='project ID (*_d4j)')

    parser.add_argument('-b', '--bid', type=int, dest='bid', default=None, help='bug ID')

    parser.add_argument('-o', '--outfile', type=str, dest='outfile', default=None,
                        metavar='FILE', help='dump result into FILE')

    args = parser.parse_args()

    if args.outfile:
        if args.outfile.endswith('.csv'):
            main_csv(args.proj_id, args.bid, args.outfile)
        else:
            main_plain(args.proj_id, args.bid, outfile=args.outfile)
    else:
        main_plain(args.proj_id, args.bid)
