#!/usr/bin/env python
import os
from smg import SMGConfigParser, SMG
from terseparse import Parser, Arg, types

description = """smg converts a configuration file into a finite state machine in C

Usage:
> smg config.c src/state_machine/
State machine written to src/state_machine/
"""


p = Parser('smg', description,
    Arg('configuration', 'file containing smg description', types.File.r),
    Arg('output-directory', 'directory to write state machine to', types.Dir.rw))

_, args = p.parse_args()

parser = SMGConfigParser()
config = parser.parse(args.ns.configuration.read())
smg = SMG(config)
smg.render(args.ns.output_directory)
config.pprint()
print('State machine successfully written to {}'.format(args.ns.output_directory))
