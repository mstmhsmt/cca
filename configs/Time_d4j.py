#!/usr/bin/env python3

import os
from cca_config import Config, get_proj_dir, VKIND_VARIANT, select

conf = Config()

conf.proj_id  = 'Time_d4j'

conf.lang = 'java'

conf.proj_path = get_proj_dir(conf.proj_id)

conf.vkind = VKIND_VARIANT

conf.include = ['src', 'source']

_BUGS = [
    [  2,  5,  6,  7,  9, ],
    [ 12, 15, 16, 17, ],
    #[21,],# bug of D4J?
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
