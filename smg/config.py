from collections import OrderedDict
from itertools import chain
import re
from StringIO import StringIO
import yaml

"""
Special Keywords in configuraiton file:
  DECLARE_STATE(name) -- declare a state type object with name *name*.
  STATE(name)         -- returns the fully qualified name of the specified state.
                         Use this when you need to refer to a state in the config.

"""
class SMGSyntaxError(Exception):
    pass


class SMGConfigNotFound(Exception):
    pass


class SMGParseError(Exception):
    pass


class SMGTransitionParseError(SMGParseError):
    pass


"""
iterable of keyword / replacement pairs
keyword can be a regex and the replacement can either be a
string or a function. If it is a function than it will be passed
the results of the regex match
"""
def kw_func(name):
    return name + r'\((\w+)\)'


class SMGNamer(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.env_name = 'm->env'
        self.state_machine_type = self('state_machine_t')
        self.state_type = self('state_t')
        self.trans_fn_type = self('trans_fn_t')
        self.state_fn_type = self('state_fn_t')
        self.transfns_array = self('trans_fns')
        self.statefns_array = self('state_fns')
        self.event_type = self('event_t')

    def __call__(self, *args):
        return '_'.join((self.prefix,) + args)

    def event_name(self, event_name):
        return self('event', event_name)

    def state_enum_name(self, state_name):
        """Returns the enum state name for name
        Example:
        >>> SMGNamer('my_smg').state_enum_name('init')
        'MY_SMG_STATE_INIT'
        """
        return self('state', state_name).upper()

    def state_fn_name(self, state_name):
        """Returns the state function for specified state
        """
        return self('state_fn', state_name)

    def trans_fn_name(self, state_name):
        """Returns the transfer function for specified state
        """
        return self('trans_fn', state_name)


class SMGTransition(object):
    def __init__(self, from_state, to_state, guards, handled_events):
        self.from_state = from_state
        self.to_state = to_state
        self.guards = guards
        self.handled_events = handled_events

    def __repr__(self):
        return '<SMGTransition from:{!r} to:{!r} guards:{!r}>'\
                .format(self.from_state.name, self.to_state.name, self.guards)


class SMGState(object):
    def __init__(self, namer, name, state_code=None):
        self.name = name
        self.enum = namer.state_enum_name(name)
        self.state_fn = namer.state_fn_name(name)
        self.trans_fn = namer.trans_fn_name(name)
        self.transitions = []
        self.state_code = state_code
        # Default transition is one with no guards
        self.default_transition = None

    def add_transition(self, to_state, guards=None, events_handled=None):
        transition = SMGTransition(self, to_state, guards, events_handled)
        if not transition.guards:
            if self.default_transition:
                raise SMGTransitionParseError('Only one transition can have no guards '\
                        'but multiple were found for state {!r}'.format(self.name))
            self.default_transition = transition
        else:
            self.transitions.append(transition)

    def __repr__(self):
        return '<SMGState name:{!r} state_code:{!r} transitions:{!r} '\
               'default_transition:{!r}>'\
               .format(self.name, self.state_code, self.transitions,
                       self.default_transition)


class SMGConfig(object):
    def __init__(self, namer, states, state_machine_env_members):
        self.namer = namer
        self.prefix = namer.prefix
        self.env_name = namer.env_name
        self.state_machine_type = namer.state_machine_type
        self.state_type = namer.state_type
        self.trans_fn_type = namer.trans_fn_type
        self.state_fn_type = namer.state_fn_type
        self.transfns_array = namer.transfns_array
        self.statefns_array = namer.statefns_array
        self.event_type = namer.event_type
        self.include_string_funcs = True
        self.include_logging = True
        self.init_code = None
        self._states = states
        self.state_machine_env_members = state_machine_env_members
        # Add special state Error
        self.error_state = SMGState(namer, 'error', 'assert(false);')
        self.error_state.add_transition(self.error_state)
        # Add special state None
        self.none_state = SMGState(namer, 'none')
        self.none_state.add_transition(self.error_state)
        self.default_state = self._states[0]

    def pprint(self):
        print('==STATE TRANSITIONS==')
        idnt = lambda n: ' ' * 4 * n
        for state in self.states:
            print(idnt(0) + '[{}]'.format(state.name))
            for tr in state.transitions:
                print(idnt(1) + '-> [{}]: {}'.format(tr.to_state.name, tr.guards))
            if state.state_code:
                print(idnt(1) + 'code:')
                print('\n'.join([idnt(2) + s.strip() for s in state.state_code.split('\n')]))

    @property
    def states(self):
        return chain([self.none_state, self.error_state], self._states)

    def __repr__(self):
        return '<SMGConfig states:{!r}>'.format(list(self.states))


class SMGConfigBuilder(object):
    def __init__(self, namer):
        self.namer = namer
        self.states = OrderedDict()
        self.env_members = None
        self.transitions = []
        self.events = set()
        self.keywords = {
            kw_func('ENV'): self._apply_env,
            kw_func('STATE'): self._apply_state,
            kw_func('ACCEPT'): self._apply_accept,
            kw_func('DECLARE_EVENT'): self._apply_declare_event,
            kw_func('DECLARE_STATE'): self._apply_declare_state,
        }

    def _apply_env(self, name):
        return self.namer.env_name + "." + name

    def _apply_state(self, name):
        return self.namer.state_enum_name(name)

    def _apply_accept(self, name):
        if name not in self.events:
            raise Exception('Event {} was not declared in ENV'.format(name))
        return self._apply_env(name)

    def _apply_declare_event(self, name):
        self.events.add(name)
        return self.namer.event_type + " " + name

    def _apply_declare_state(self, name):
        return self.namer.state_type + " " + name

    def _apply_keywords(self, txt):
        """Apply keywords functions to block of txt"""
        for pattern, fn in self.keywords.iteritems():
            txt = re.sub(pattern, lambda m: fn(m.group(1)), txt)
        return txt

    def add_state(self, name):
        if name not in self.states:
            self.states[name] = SMGState(self.namer, name)
        return self.states[name]

    def add_env_members(self, members):
        members = members or ''
        members = self._apply_keywords(members)
        self.env_members = members

    def add_state_body(self, state_name, code):
        code = code or ''
        code = self._apply_keywords(code)
        state = self.add_state(state_name)
        state.state_code = code

    def _get_handled_events(self, guards):
        return set(m.group(1) for m in re.finditer(kw_func('ACCEPT'), guards))

    def add_transition(self, from_name, to_name, guards):
        guards = guards or ''
        from_state = self.add_state(from_name)
        to_state = self.add_state(to_name)
        events = self._get_handled_events(guards)
        guards = self._apply_keywords(guards)
        from_state.add_transition(to_state, guards, events)

    @property
    def config(self):
        return SMGConfig(self.namer,
                         self.states.values(),
                         self.env_members)
