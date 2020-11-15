#!/usr/bin/env python3

from cca_config import Config, get_proj_dir, VKIND_VARIANT, select

conf = Config()

conf.proj_id  = 'hsqldb_ddj'

conf.lang = 'java'

conf.proj_path = get_proj_dir(conf.proj_id)

conf.vkind = VKIND_VARIANT

conf.include = [
    'src',
]

EXAMPLES = [ 933, 1454, ]

EXAMPLES = select('DD_EXAMPLE_NUM', EXAMPLES)

conf.vpairs = [('%dg' % x, '%db' % x) for x in EXAMPLES]

conf.vers = [x for l in conf.vpairs for x in l]

conf.optout_tbl = {
    ('933g','933b') : [('DEL', 847, 4, 854, 4, 'src/org/hsqldb/ExpressionColumn.java',
                    51, 49, 822, 0, 'src/org/hsqldb/ExpressionColumn.java'),

                   ('DEL', 470, 16, 482, 16, 'src/org/hsqldb/RangeVariableResolver.java',
                    387, 49, 397, 12, 'src/org/hsqldb/RangeVariableResolver.java'),
    ],
}

conf.get_long_name = lambda x: x

conf.finalize()
