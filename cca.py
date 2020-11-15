#!/usr/bin/env python3

'''
  A driver script for CCA container image

  Copyright 2020 Codinuum Software Lab <https://codinuum.com>

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

import os
import sys
import time
import shutil
from datetime import datetime, timedelta
from subprocess import Popen, run
from threading import Thread
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

#IMAGE_NAME = 'codinuum/cca'
#IMAGE_NAME = 'codecontinuum/ddj'
IMAGE_NAME = 'ddjx'

#

CCA_HOME = '/opt/cca'
CCA_VAR = '/var/lib/cca'
CCA_LOG_DIR = '/var/log/cca'

CCA_SOURCE_DIR = CCA_VAR+'/source'
CCA_CACHE_DIR = CCA_VAR+'/cache'

CCA_WORK_DIR_NAME = '__CCA__'

CONTAINER_CMD = 'docker'

DEPENDENCIES_INSTALLER = 'install_dependencies.sh'

TIMEOUT = 5
BUFSIZE = 0 # unbuffered
STAT_NAME = 'status'

DEFAULT_CACHE_DIR = os.path.join(os.environ['HOME'], '.cca', 'cache')

#WIN_HOST_FLAG = sys.platform.startswith('win')

### timezone

TZ = None

if time.timezone != 0:
    SIGN = '+' if time.timezone > 0 else '-'

    STDOFFSET = timedelta(seconds=-time.timezone)
    if time.daylight:
        DSTOFFSET = timedelta(seconds=-time.altzone)
    else:
        DSTOFFSET = STDOFFSET

    dt = datetime.now()
    tt = (dt.year, dt.month, dt.day,
          dt.hour, dt.minute, dt.second,
          dt.weekday(), 0, 0)
    stamp = time.mktime(tt)
    tt = time.localtime(stamp)

    isdst = tt.tm_isdst > 0

    tzname = None
    offset = 0

    if isdst:
        tzname = time.tzname[1]
        offset = DSTOFFSET
    else:
        tzname = time.tzname[0]
        offset = STDOFFSET

    TZ = '{}{}{}'.format(tzname, SIGN, offset)

###

def progress(proc, stat_path, timeout=TIMEOUT):
    stat_mtime = None

    print('\nMonitoring thread started.')

    while True:
        try:
            st = os.stat(stat_path)
            if st.st_mtime != stat_mtime and st.st_size > 0:
                with open(stat_path, 'r') as f:
                    mes = f.read()
                    print('[{}]'.format(mes))

                stat_mtime = st.st_mtime

        except OSError as e:
            pass

        if proc.poll() is not None:
            break

    proc.wait()
    if proc.returncode > 0:
        print('Execution failed: {}'.format(proc.returncode))

def ensure_dir(dpath):
    if not os.path.isdir(dpath):
        try:
            os.makedirs(dpath)
        except Exception as e:
            raise

def get_image_name(image_name, devel=False):
    suffix = ''
    if devel:
        suffix = ':devel'
    image = image_name+suffix
    return image

def run_diffast(container_cmd, original, modified, cache=DEFAULT_CACHE_DIR, clear_cache=False, view=False,
                dry_run=False, devel=False, image=IMAGE_NAME, verbose=False, debug=False):

    if dry_run:
        verbose = True

    original = os.path.abspath(original)
    modified = os.path.abspath(modified)
    cache = os.path.abspath(cache)

    if not dry_run:
        ensure_dir(cache)

    cca_cmd_path = '{}/bin/{}.opt'.format(CCA_HOME, 'diffast')
    cca_cmd = cca_cmd_path
    if clear_cache:
        cca_cmd += ' -clearcache'

    cca_cmd += ' -cache {}'.format(CCA_CACHE_DIR)

    orig_dir = os.path.dirname(original)
    mod_dir = os.path.dirname(modified)

    common_path = os.path.commonpath([orig_dir, mod_dir])

    orig_path = CCA_SOURCE_DIR+'/'+os.path.relpath(original, start=common_path)
    mod_path = CCA_SOURCE_DIR+'/'+os.path.relpath(modified, start=common_path)

    cca_cmd += ' {} {}'.format(orig_path, mod_path)

    vol_opt = '-v "{}:{}"'.format(common_path, CCA_SOURCE_DIR)
    vol_opt += ' -v "{}:{}"'.format(cache, CCA_CACHE_DIR)

    run_cmd = '{} run'.format(container_cmd)
    run_cmd += ' --rm'
    run_cmd += ' -t'

    if TZ:
        run_cmd += ' -e "TZ={}"'.format(TZ)

    run_cmd += ' {}'.format(vol_opt)
    run_cmd += ' {} {}'.format(get_image_name(image, devel=devel), cca_cmd)

    if verbose:
        print(run_cmd)

    if not dry_run:
        try:
            rc = run(run_cmd, bufsize=BUFSIZE, shell=True, universal_newlines=True)

            if view:
                app_path = os.path.join(os.path.dirname(sys.argv[0]),
                                        'diffviewer',
                                        'DiffViewer-darwin-x64',
                                        'DiffViewer.app')
                if os.path.exists(app_path):
                    cache_opt = ' --cache {}'.format(cache)
                    files_opt = ' --file0 {} --file1 {}'.format(original, modified)
                    view_cmd = 'open -n {} --args{}{}'.format(app_path, cache_opt, files_opt)
                    if verbose:
                        print(view_cmd)
                    rc = run(view_cmd, shell=True)
                else:
                    print('DiffViewer not found. See diffviewer/README.md.')

        except (KeyboardInterrupt, SystemExit):
            print('Interrupted.')

        except OSError as e:
            print('Execution failed: {}'.format(e))


def run_dd(container_cmd, engine, proj_dir, v_good, v_bad, build_script='build.sh', test_script='test.sh',
           proj_id=None, include=[], lang=[], algo='ddmin',
           shuffle=False, greedy=False, staged=False,
           dry_run=False, devel=False, image=IMAGE_NAME, verbose=True, debug=False, **kwargs):
    if dry_run:
        verbose = True

    if proj_id == None:
        proj_id = os.path.basename(proj_dir)

    proj_dir = os.path.abspath(proj_dir)

    work_dir = os.path.join(proj_dir, CCA_WORK_DIR_NAME)
    v_good_dir = os.path.join(proj_dir, v_good)
    v_bad_dir = os.path.join(proj_dir, v_bad)

    if not dry_run:
        if os.path.exists(v_good_dir):
            test_script_path = os.path.join(v_good_dir, test_script)
            if not os.path.exists(test_script_path):
                print('Test script not found: {}'.format(test_script_path))
        else:
            print('v_good not found: {}'.format(v_good_dir))
            return

        if not os.path.exists(v_bad_dir):
            print('v_bad not found: {}'.format(v_bad_dir))
            return

        if os.path.exists(work_dir):
            print('You are about to overwrite "{}".'.format(work_dir))
            while True:
                a = input('Do you want to proceed (y/n)? ')
                if a == 'y':
                    break
                elif a == 'n':
                    return
        else:
            ensure_dir(work_dir)

    cca_proj_dir = CCA_VAR+'/project'

    cca_cmd = '{}/ddutil/{}.py'.format(CCA_HOME, engine)
    cca_cmd += ' {} {} {}'.format(cca_proj_dir, v_good, v_bad)
    cca_cmd += ' --build-script {} --test-script {}'.format(build_script, test_script)
    cca_cmd += ' --proj-id {}'.format(proj_id)
    if include:
        cca_cmd += ''.join([' --include {}'.format(i) for i in include])
    if lang:
        cca_cmd += ''.join([' --lang {}'.format(i) for i in lang])
    cca_cmd += ' -a {}'.format(algo)
    if shuffle:
        cca_cmd += ' --shuffle'
    if greedy:
        cca_cmd += ' --greedy'
    if staged:
        cca_cmd += ' --staged'
    if debug:
        cca_cmd += ' -d'
    elif verbose:
        cca_cmd += ' -v'


    if kwargs.get('custom_split', False):
        cca_cmd += ' --custom-split'
    max_stmt_level = kwargs.get('max_stmt_level', None)
    modified_stmt_rate_thresh = kwargs.get('modified_stmt_rate_thresh', None)
    mem = kwargs.get('mem', None)
    if max_stmt_level != None:
        cca_cmd += ' --max-stmt-level {}'.format(max_stmt_level)
    if modified_stmt_rate_thresh != None:
        cca_cmd += ' --modified-stmt-rate-thresh {}'.format(modified_stmt_rate_thresh)
    if mem != None:
        cca_cmd += ' --mem {}'.format(mem)

    cca_cmd = '/bin/bash -c "(time {}) >& {}/{}.log"'.format(cca_cmd, CCA_VAR, engine)

    run_cmd = '{} run --rm -t'.format(container_cmd)
    vol_opt = ' -v "{}:{}"'.format(proj_dir, cca_proj_dir)
    vol_opt += ' -v "{}:{}"'.format(work_dir, CCA_VAR)
    installer_path = os.path.join(proj_dir, DEPENDENCIES_INSTALLER)
    if os.path.exists(installer_path):
        vol_opt += ' -v "{}:{}"'.format(installer_path, cca_proj_dir+'/'+DEPENDENCIES_INSTALLER)

    if TZ:
        run_cmd += ' -e "TZ={}"'.format(TZ)

    run_cmd += vol_opt
    run_cmd += ' {} {}'.format(get_image_name(image, devel=devel), cca_cmd)

    stat_path = os.path.join(work_dir, STAT_NAME)

    if verbose:
        print(run_cmd)

    if not dry_run:

        if os.path.exists(stat_path):
            #print('Removing "{}"...'.format(stat_path))
            os.remove(stat_path)

        try:
            proc = Popen(run_cmd, bufsize=BUFSIZE, shell=True, universal_newlines=True)
            th = Thread(target=progress, args=(proc, stat_path))
            th.start()
            th.join()

        except (KeyboardInterrupt, SystemExit):
            print('Interrupted.')

        except OSError as e:
            print('Execution failed: {}'.format(e))


def run_ddplain(container_cmd, proj_dir, v_good, v_bad, build_script='build.sh', test_script='test.sh',
                proj_id=None, include=[], lang=[], algo='ddmin',
                shuffle=False, greedy=False, staged=False,
                dry_run=False, devel=False, image=IMAGE_NAME, verbose=True, debug=False):
    run_dd(container_cmd, 'ddp', proj_dir, v_good, v_bad, build_script=build_script, test_script=test_script,
           proj_id=proj_id, include=include, lang=lang, algo=algo,
           shuffle=shuffle, greedy=greedy, staged=staged,
           dry_run=dry_run, devel=devel, image=image, verbose=verbose, debug=debug)

def run_ddjava(container_cmd, proj_dir, v_good, v_bad, build_script='build.sh', test_script='test.sh',
               proj_id=None, include=[], algo='ddmin',
               shuffle=False, greedy=False, staged=False,
               custom_split=False, max_stmt_level=8,
               modified_stmt_rate_thresh=0.05, mem=8,
               dry_run=False, devel=False, image=IMAGE_NAME, verbose=False, debug=False):
    run_dd(container_cmd, 'ddj', proj_dir, v_good, v_bad, build_script=build_script, test_script=test_script,
           proj_id=proj_id, include=include, lang=[], algo=algo,
           shuffle=shuffle, greedy=greedy, staged=staged,
           custom_split=custom_split, max_stmt_level=max_stmt_level,
           modified_stmt_rate_thresh=modified_stmt_rate_thresh, mem=mem,
           dry_run=dry_run, devel=devel, image=image, verbose=verbose, debug=debug)


def update(args):
    cmd = '{} pull {}'.format(args.container_cmd, get_image_name(args.image, devel=args.devel))
    if args.verbose or args.dry_run:
        print(cmd)
    if not args.dry_run:
        try:
            run(cmd, shell=True)
        except OSError as e:
            print('Execution failed: {}'.format(e))

def diffast(args):
    run_diffast(args.container_cmd,
                args.original, args.modified, cache=args.cache, clear_cache=args.force, view=args.view,
                dry_run=args.dry_run, devel=args.devel, image=args.image, verbose=args.verbose, debug=args.debug)

def ddplain(args):
    run_ddplain(args.container_cmd,
                args.proj_dir, args.v_good, args.v_bad, args.build_script, args.test_script,
                proj_id=args.proj_id, include=args.include, lang=args.lang, algo=args.algo,
                shuffle=args.shuffle, greedy=args.greedy, staged=args.staged,
                dry_run=args.dry_run, devel=args.devel, image=args.image, verbose=args.verbose, debug=args.debug)

def ddjava(args):
    run_ddjava(args.container_cmd,
               args.proj_dir, args.v_good, args.v_bad, args.build_script, args.test_script,
               proj_id=args.proj_id, include=args.include, algo=args.algo,
               shuffle=args.shuffle, greedy=args.greedy, staged=args.staged,
               custom_split=args.custom_split, max_stmt_level=args.max_stmt_level,
               modified_stmt_rate_thresh=args.modified_stmt_rate_thresh, mem=args.mem,
               dry_run=args.dry_run, devel=args.devel, image=args.image, verbose=args.verbose, debug=args.debug)



def main():
    parser = ArgumentParser(description='CCA driver',
                            add_help=False,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-n', '--dry-run', dest='dry_run', action='store_true',
                        help='only print container commands')

    parser.add_argument('--container-command', dest='container_cmd', metavar='CMD',
                        help='specify container command', default=CONTAINER_CMD)

    parser.add_argument('--image', dest='image', type=str, metavar='IMAGE', default=IMAGE_NAME,
                        help='specify container image')

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='enable verbose printing')

    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='enable debug printing')

    parser.add_argument('-x', '--experimental', dest='devel', action='store_true',
                        help='use experimental image')

    p = ArgumentParser(add_help=False)
    subparsers = p.add_subparsers(title='subcommands')

    # Docker image update

    parser_update = subparsers.add_parser('update',
                                          description='Update docker image of CCA',
                                          parents=[parser],
                                          formatter_class=ArgumentDefaultsHelpFormatter)

    parser_update.set_defaults(func=update)

    # Diff/AST

    parser_diffast = subparsers.add_parser('diffast',
                                           description='Compare two programs',
                                           parents=[parser],
                                           formatter_class=ArgumentDefaultsHelpFormatter)

    parser_diffast.add_argument('original', type=str, metavar='ORIGINAL', help='original source file')

    parser_diffast.add_argument('modified', type=str, metavar='MODIFIED', help='modified source file')

    parser_diffast.add_argument('--view', dest='view', action='store_true',
                                help='launch DiffViewer after comparison')

    parser_diffast.add_argument('-f', '--force', dest='force', action='store_true',
                                help='force comparison (overwrite cache)')

    parser_diffast.add_argument('-c', '--cache', dest='cache', default=DEFAULT_CACHE_DIR,
                                 metavar='DIR', type=str, help='result cache directory')

    parser_diffast.set_defaults(func=diffast)

    # DDP

    parser_ddp = subparsers.add_parser('ddplain',
                                       description='Delta debugging on changes of (plain text) programs',
                                       parents=[parser],
                                       formatter_class=ArgumentDefaultsHelpFormatter)

    parser_ddp.add_argument('proj_dir', type=str, help='project directory')
    parser_ddp.add_argument('v_good', type=str, help='id of good version (proj_dir/v_good)')
    parser_ddp.add_argument('v_bad', type=str, help='id of bad version (proj_dir/v_bad)')

    parser_ddp.add_argument('--build-script', type=str, default='build.sh',
                            help='specify build script at proj_dir/v_good/')

    parser_ddp.add_argument('--test-script', type=str, default='test.sh',
                            help='specify script at proj_dir/v_good/ that returns test result (PASS|FAIL|UNRESOLVED)')

    parser_ddp.add_argument('--proj-id', type=str, metavar='PROJ_ID', default=None,
                            help='project id (dirname of PROJ_DIR is used by default)')

    parser_ddp.add_argument('--include', type=str, metavar='DIR', action='append', default=[],
                            help='analyze only sub-directories (relative paths)')

    parser_ddp.add_argument('--lang', type=str, metavar='LANG', action='append', choices=['java', 'python'],
                            help='specify languages {%(choices)s}')

    parser_ddp.add_argument('-a', '--algo', dest='algo', choices=['ddmin', 'dd'],
                            help='specify DD algorithm', default='ddmin')

    parser_ddp.add_argument('--shuffle', dest='shuffle', type=int, metavar='N', default=0,
                            help='shuffle delta components N times')

    parser_ddp.add_argument('--greedy', dest='greedy', action='store_true',
                            help='try to find multiple solutions')

    parser_ddp.add_argument('--staged', dest='staged', action='store_true',
                            help='enable staging')

    parser_ddp.set_defaults(func=ddplain)

    # DDJ

    parser_ddj = subparsers.add_parser('ddjava',
                                       description='Delta debugging on changes of Java programs',
                                       parents=[parser],
                                       formatter_class=ArgumentDefaultsHelpFormatter)

    parser_ddj.add_argument('proj_dir', type=str, help='project directory')
    parser_ddj.add_argument('v_good', type=str, help='id of good version (proj_dir/v_good)')
    parser_ddj.add_argument('v_bad', type=str, help='id of bad version (proj_dir/v_bad)')

    parser_ddj.add_argument('--build-script', type=str, default='build.sh',
                            help='specify build script at proj_dir/v_good/')

    parser_ddj.add_argument('--test-script', type=str, default='test.sh',
                            help='specify script at proj_dir/v_good/ that returns test result (PASS|FAIL|UNRESOLVED)')

    parser_ddj.add_argument('--proj_id', type=str, metavar='PROJ_ID', default=None,
                            help='specify project id (dirname of PROJ_DIR is used by default)')

    parser_ddj.add_argument('--include', type=str, metavar='DIR', action='append', default=[],
                            help='analyze only sub-directories (relative paths)')

    parser_ddj.add_argument('-a', '--algo', dest='algo', choices=['ddmin', 'dd'],
                            help='specify DD algorithm', default='ddmin')

    parser_ddj.add_argument('--shuffle', dest='shuffle', type=int, metavar='N', default=0,
                            help='shuffle delta components N times')

    parser_ddj.add_argument('--greedy', dest='greedy', action='store_true',
                            help='try to find multiple solutions')

    parser_ddj.add_argument('--staged', dest='staged', action='store_true',
                            help='enable staging')

    parser_ddj.add_argument('--custom-split', dest='custom_split', action='store_true',
                            help='enable custom split')

    parser_ddj.add_argument('--max-stmt-level', dest='max_stmt_level', default=8,
                            metavar='N', type=int, help='grouping statements at levels up to N')

    parser_ddj.add_argument('--modified-stmt-rate-thresh', dest='modified_stmt_rate_thresh',
                            default=0.05, metavar='R', type=float,
                            help='suppress level 1+ statement grouping when modified statement rate is less than R')

    parser_ddj.add_argument('-m', '--mem', dest='mem', metavar='GB', type=int,
                            choices=[2, 4, 8, 16, 32, 48, 64], default=8,
                            help='set available memory (GB) for container')

    parser_ddj.set_defaults(func=ddjava)

    #

    args = p.parse_args()

    try:
        args.func(args)
    except:
        raise
        parser.print_help()


if __name__ == '__main__':
    main()
