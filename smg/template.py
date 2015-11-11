from collections import namedtuple


Transition = namedtuple('Transition', [
    'state',
    'guards'])

State = namedtuple('State', [
    'name',
    'enum',
    'state_fn_name',
    'trans_fn_name',
    'state_code',
    'transitions'])

StateMachineConfig = namedtuple('StateMachineConfig', [
    'prefix',
    'state_machine_type',
    'state_type',
    'states',
    'trans_fn_type',
    'state_fn_type',
    'trans_fns',
    'state_fns',
    'include_string_funcs',
    'include_logging',
    'init_code',
    'error_state',
    'none_state'])
