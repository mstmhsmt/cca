#!/usr/bin/env python

from cca_config import Config, get_proj_dir, VKIND_VARIANT, select

conf = Config()

conf.proj_id  = 'antlr_ddj'

conf.lang = 'java'

conf.proj_path = get_proj_dir(conf.proj_id)

conf.vkind = VKIND_VARIANT

conf.include = [
    'tool/src',
    #'antlr4-maven-plugin/src/main/java',
]

EXAMPLES = [ 1543, ]

EXAMPLES = select('DD_EXAMPLE_NUM', EXAMPLES)

conf.vpairs = [('%dg' % x, '%db' % x) for x in EXAMPLES]

conf.vers = [x for l in conf.vpairs for x in l]

conf.get_long_name = lambda x: x

conf.finalize()
