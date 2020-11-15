#!/usr/bin/env python3

import os
from cca_config import Config, get_proj_dir, VKIND_VARIANT, select

conf = Config()

conf.proj_id  = 'Mockito_d4j'

conf.lang = 'java'

conf.proj_path = get_proj_dir(conf.proj_id)

conf.vkind = VKIND_VARIANT

conf.include = ['src', 'source', 'test']

_BUGS = [
    [  2,  3,  4,  5,  6, ],
    [  7, 10, 11, 14, 15, ],
    [ 16, 17, 18, 19, 20, ],
    [ 21, 23, 25, 26, 27, ],
    [ 28, 29, 30, 31, 33, ],
    [ 34, 35, 36, 37, 38, ],
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
