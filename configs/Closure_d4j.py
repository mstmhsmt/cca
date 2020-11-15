#!/usr/bin/env python3

import os
from cca_config import Config, get_proj_dir, VKIND_VARIANT, select

conf = Config()

conf.proj_id  = 'Closure_d4j'

conf.lang = 'java'

conf.proj_path = get_proj_dir(conf.proj_id)

conf.vkind = VKIND_VARIANT

conf.include = ['src', 'source']

_BUGS = [
    [  2,  4,  6,  9, 10, ],
    [ 12, 13, 16, 21, 22, ],
    [ 23, 26, 27, 28, 30, ],
    [ 32, 34, 35, 36, 38, ],
    [ 41, 43, 45, 46, 47, ],
    [ 48, 49, 50, 51, 54, ],
    [ 55, 56, 57, 60, 69, ],
    [ 72, 74, 75, 76, 78, ],
    [ 79, 84, 85, 87, 88, ],
    [ 90, 95, 96, 98, 99, ],
    [ 100, 101, 102, 103, 104, ],
    [ 107, 109, 110, 112, 114, ],
    [ 117, 118, 121, 122, 123, ],
    [ 124, 125, 131, 133, ],
]

_pn = os.getenv('DD_PART_NUM', '')
if _pn:
    try:
        pn = int(_pn)
        BUGS = _BUGS[pn]
    except:
        print('! invalid part number: "{}"'.format(_pn))
else:
    BUGS = [ x for l in _BUGS for x in l ]

BUGS = select('DD_EXAMPLE_NUM', BUGS)

conf.vpairs = [('{}f'.format(x), '{}p'.format(x)) for x in BUGS]

conf.vers = [x for l in conf.vpairs for x in l]

conf.get_long_name = lambda x: x

conf.finalize()
