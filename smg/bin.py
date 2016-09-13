from __future__ import absolute_import

import sys

from terseparse import Parser, Arg, types

from smg import __version__
from smg import SMG

description = """smg converts a configuration file into a finite state machine in C

Usage:
> smg config.h src/state_machine/
State machine written to src/state_machine/
"""


p = Parser('smg', description,
    Arg('--version', 'smg tool version', action='version', version='%(prog)s ({})'.format(__version__)),
    Arg('configuration', 'file containing smg description', types.File.r),
    Arg('output-directory', 'directory to write state machine to', types.Dir.rw | '-'))

def main():
    _, args = p.parse_args()
    smg = SMG.from_file(args.ns.configuration)
    path = args.ns.output_directory
    path = sys.stdout if path == '-' else path
    smg.render(path)
    print('State machine successfully written to {}'.format(args.ns.output_directory))
