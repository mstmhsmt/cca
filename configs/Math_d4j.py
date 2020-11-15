#!/usr/bin/env python3

import os
from cca_config import Config, get_proj_dir, VKIND_VARIANT, select

conf = Config()

conf.proj_id  = 'Math_d4j'

conf.lang = 'java'

conf.proj_path = get_proj_dir(conf.proj_id)

conf.vkind = VKIND_VARIANT

conf.include = ['src', 'source']

_BUGS = [
    [  1,  7,  8,  9, 13, ],
    [ 14, 16, 19, 20, 21, ],
    [ 23, 24, 25, 28, 30, ],
    [ 31, 36, 38, 44, 45, ],
    [ 47, 48, 51, 52, 55, ],
    [ 58, 60, 61, 62, 63, ],
    [ 64, 65, 66, 71, 73, ],
    [ 74, 76, 77, 78, 81, ],
    [ 82, 83, 84, 88, 90, ],
    [ 91, 93, 95, 97, ],
    [ 99, 102, 103, 104, ],
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
