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
    for state_fn in cfg['state_fns']:
        b.add_state_body(state_fn);
    return b.config


class SMG(object):
    config_defaults = {
        'prefix': 'smg',
        'env': None,
        'transitions': [],
        'state_fns': []
    }

    def __init__(self, template_config):
        self.config = template_config

    @staticmethod
    def from_file(file):
        config = parse(file.read())
        return SMG(template_config(config, SMG.config_defaults))

    def render(self, output_dir):
        for tmpl, name in [('header.h', '{}.h'),
                           ('source.c', '{}.c')]:
            name = name.format(self.config.prefix)
            template = env.get_template(tmpl)
            txt = template.render(smg=self.config)
            with open(os.path.join(output_dir, name), 'w') as f:
                f.write(txt)
