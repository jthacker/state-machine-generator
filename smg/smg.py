from __future__ import absolute_import

from collections import namedtuple
from itertools import chain
from jinja2 import Environment, PackageLoader
import os

from .config import SMGConfigBuilder, SMGNamer
from .parser import parse

env = Environment(loader=PackageLoader('smg', 'templates'),
                  trim_blocks=True,
                  lstrip_blocks=True)




def template_config(cfg, defaults):
    """Build a template configuration the state machine configuration"""
    cfg = {k: v or defaults[k] for k, v in cfg.iteritems()}
    b = SMGConfigBuilder(SMGNamer(cfg['prefix']))
    # Add env members
    b.add_env_members(cfg['env'])
    # Add transitions
    for from_state, to_state, guards in cfg['transitions']:
        b.add_state(from_state)
        b.add_state(to_state)
        b.add_transition(from_state, to_state, guards)
    # Add state function bodies
    for state_name, state_fn in cfg['state_fns'].iteritems():
        b.add_state_body(state_name, state_fn);
    return b.config


class SMG(object):
    config_defaults = {
        'prefix': 'smg',
        'env': None,
        'transitions': [],
        'state_fns': []
    }

    def __init__(self, config):
        self.config = config

    @staticmethod
    def from_file(file):
        config = parse(file.read())
        return SMG(template_config(config, SMG.config_defaults))

    def render(self, output_path):
        """Render a statemachine to output_path
        Args:
            output_path -- can be either a path string to a directory
                           or an object that supports write
        """
        for tmpl, name in [('header.h', '{}.h'),
                           ('source.c', '{}.c')]:
            name = name.format(self.config.prefix)
            template = env.get_template(tmpl)
            txt = template.render(smg=self.config)
            if isinstance(output_path, basestring):
                out = open(os.path.join(output_path, name), 'w')
            else:
                out = output_path
            out.write(txt)
