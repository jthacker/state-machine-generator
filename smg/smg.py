from collections import namedtuple
from itertools import chain
from jinja2 import Environment, PackageLoader
import os

from .template import Transition, State, StateMachineConfig


env = Environment(loader=PackageLoader('smg', 'templates'),
                  trim_blocks=True,
                  lstrip_blocks=True)


class SMG(object):
    def __init__(self, config):
        self.config = config

    def render(self, output_dir):
        for tmpl, name in [('header.h', '{}.h'),
                           ('source.c', '{}.c')]:
            name = name.format(self.config.prefix)
            template = env.get_template(tmpl)
            txt = template.render(smg=self.config)
            with open(os.path.join(output_dir, name), 'w') as f:
                f.write(txt)
