#!/usr/bin/env python3

'''
  overlap.py

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
from difflib import SequenceMatcher
from javalang import tokenizer



def get_tokens(path):
    toks = []
    try:
        with open(path, 'r') as f:
            for tok in tokenizer.tokenize(f.read()):
                toks.append(tok.value)
    except Exception as e:
        pass

    seq = []

    while True:
        try:
            tok = toks.pop(0)

            if tok == '.':
                try:
                    nxt = toks.pop(0)
                    r = '.' + nxt
                    if seq:
                        seq[-1] += r
                    else:
                        seq.append(r)

                except IndexError:
                    seq.append(tok)

            else:
                seq.append(tok)

        except IndexError:
            break

    return seq

def meet_of_tokens(toks1, toks2): # returns index set (left toks)
    m = SequenceMatcher(isjunk=None, a=toks1, b=toks2, autojunk=False)
    toks = set()
    for nt in m.get_matching_blocks():
        for i in range(nt.a, nt.a+nt.size):
            toks.add(i)
    return toks

def insert_of_tokens(toks1, toks2): # returns index * token list
    m = SequenceMatcher(isjunk=None, a=toks1, b=toks2, autojunk=False)
    ins_tbl = {}
    for (tag, i1, _, j1, j2) in m.get_opcodes():
        if tag in ('insert', 'replace'):
            ins_tbl[i1] = toks2[j1:j2]
    return ins_tbl

def overlap_of_insert(base_toks, toks1, toks2):
    ib1 = insert_of_tokens(base_toks, toks1)
    ib2 = insert_of_tokens(base_toks, toks2)
    o = 0
    for (i, insl1) in ib1.items():
        try:
            insl2 = ib2[i]
            m = SequenceMatcher(isjunk=None, a=insl1, b=insl2, autojunk=False)
            for nt in m.get_matching_blocks():
                o += nt.size
        except KeyError:
            pass

    return o

def diff_tokens(toks1, toks2):
    m = SequenceMatcher(isjunk=None, a=toks1, b=toks2, autojunk=False)
    d = {'replace':[],'delete':[],'insert':[]}
    for (tag, i1, i2, j1, j2) in m.get_opcodes():
        if tag != 'equal':
            d[tag].append(((i1, i2), (j1, j2)))
    return d

def overlap_of_ranges(a1_b1, a2_b2):
    a1, b1 = a1_b1
    a2, b2 = a2_b2
    s = max(a1, a2)
    e = min(b1, b2)
    o = e - s
    if o < 0:
        o = 0
    return o

def overlap_of_delete(dels1, dels2):
    o = 0
    for (r1, r2) in dels1:
        for (r3, r4) in dels2:
            o += overlap_of_ranges(r1, r3)
    return o

def overlap_of_replace(repls1, repls2, toks1, toks2):
    o = 0
    for (r1, r2) in repls1:
        (a1, b1) = r2
        x = toks1[a1:b1]
        for (r3, r4) in repls2:
            (a2, b2) = r4
            y = toks2[a2:b2]
            if x == y:
                o += overlap_of_ranges(r1, r3)
    return o

def size_of_diff(d):
    sz = 0
    for ((i1, i2), _) in d['delete']:
        sz += i2 - i1

    for ((i1, i2), (j1, j2)) in d['replace']:
        sz += i2 - i1 + j2 - j1

    for (_, (j1, j2)) in d['insert']:
        sz += j2 - j1

    return sz

def diff_to_str(d, toks1, toks2):
    dels = d['delete']
    repls = d['replace']
    inss = d['insert']

    lines = []

    if dels:
        for ((a, b), _) in dels:
            lines.append('[DELETE] %d-%d (%d):\n' % (a, b-1, b-a))
            lines.append(' '.join(toks1[a:b]))
            lines.append('\n')
    if repls:
        for ((a, b), (a2, b2)) in repls:
            lines.append('[REPLACE] %d-%d -> %d-%d (%d->%d):\n' % (a, b-1, a2, b2-1, b-a, b2-a2))
            lines.append(' '.join(toks1[a:b]))
            lines.append('\n-----\n')
            lines.append(' '.join(toks2[a2:b2]))
            lines.append('\n')
    if inss:
        for ((i, _), (a, b)) in inss:
            lines.append('[INSERT] %d -> %d-%d (%d):\n' % (i, a, b-1, b-a))
            lines.append(' '.join(toks2[a:b]))
            lines.append('\n')

    s = ''.join(lines)

    return s

def print_diff(d, toks1, toks2):
    print(diff_to_str(d, toks1, toks2))

def get_overlap_info(base_file, file1, file2, quiet=True):
    base_toks = get_tokens(base_file)
    toks1 = get_tokens(file1)
    toks2 = get_tokens(file2)

    if file1 == None:
        toks1 = base_toks

    if file2 == None:
        toks2 = base_toks

    same = toks1 == toks2

    d1 = diff_tokens(base_toks, toks1)
    d2 = diff_tokens(base_toks, toks2)

    sz1 = size_of_diff(d1)
    sz2 = size_of_diff(d2)

    diff1 = ''
    diff2 = ''

    if same:
        o = sz1
    else:
        if not quiet:
            print('*** diff1:')
            diff1 = diff_to_str(d1, base_toks, toks1)
            print(diff1)

            print('')

            print('*** diff2:')
            diff2 = diff_to_str(d2, base_toks, toks2)
            print(diff2)

            print('')

        dels1 = d1['delete'] + d1['replace']
        dels2 = d2['delete'] + d2['replace']
        o0 = overlap_of_delete(dels1, dels2)
        if not quiet:
            print('overlap_of_delete_or_replace: %d' % o0)

        o1 = overlap_of_insert(base_toks, toks1, toks2)
        if not quiet:
            print('overlap_of_insert_or_replace: %d' % o1)

        o = o0 + o1

    info = {'same':same,'left':sz1,'right':sz2,'overlap':o,'diff1':diff1,'diff2':diff2}

    return info


if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='count overlaps between patches',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('base_file', type=str)
    parser.add_argument('file1', type=str)
    parser.add_argument('file2', type=str)

    args = parser.parse_args()

    info = get_overlap_info(args.base_file, args.file1, args.file2, quiet=False)

    print('|diff1|=%(left)d, |diff2|=%(right)d, overlap=%(overlap)d' % info)

