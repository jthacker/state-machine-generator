from collections import OrderedDict
from itertools import chain
import re
from StringIO import StringIO
import yaml

"""
Special Keywords in configuraiton file:
  DECLARE_ENV         -- body is used to declare the members of the env struct
                         env is accessible in state bodies through m->env

  DECLARE_EVENT(name) -- declare an event object. Event objects are treated specially
                         by the state machine. After an even has been handled it
                         will automatically be unset. Equivalent to a boolean.

  DECLARE_STATE(name) -- declare a state type object with name *name*.

  STATE_FN(name)      -- define a state function for the state with named *name*
                         body is C code that will be executed when state is entered

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
    return name+'\((\w+)\)'

KEYWORDS = {
    'DECLARE_ENV': '',
    kw_func('STATE_FN'): '',
}


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
    def __init__(self, from_state, to_state, guards):
        self.from_state = from_state
        self.to_state = to_state
        self.guards = guards

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

    def add_transition(self, to_state, guards=None):
        transition = SMGTransition(self, to_state, guards)
        if not transition.guards:
            if self.default_transition:
                raise SMGTransitionParseError('Only one transition can have no guards '\
                        'but multiple were found for state {!r}'.format(self.name))
            self.default_transition = transition
        else:
            self.transitions.append(transition)

    def __repr__(self):
        return '<SMGState name:{!r} state_code:{!r} transitions:{!r}'\
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
        self.transitions = OrderedDict()
        self.events = set()
        self.keywords = {
            'ENV': namer.env_name,
            kw_func('STATE'): lambda m: self._apply_state(m.group(1)),
            kw_func('DECLARE_EVENT'): lambda m: self._apply_declare_event(m.group(1)),
            kw_func('DECLARE_STATE'): lambda m: self._apply_declare_state(m.group(1)),
        }

    def _apply_state(self, name):
        return self.namer.state_enum_name(name)

    def _apply_declare_event(self, name):
        self.events.add(name)
        return self.namer.event_type + " " + name

    def _apply_declare_state(self, name):
        return self.namer.state_type + " " + name

    def apply_keywords(self, txt):
        """Apply keywords functions to block of txt"""
        for pattern, val in self.keywords.iteritems():
            txt = re.sub(pattern, val, txt)
        return txt

    def add_state(self, name):
        if name not in self.states:
            self.states[name] = SMGState(self.namer, name)
        return self.states[name]

    def add_env_members(self, members):
        members = self.apply_keywords(members)
        self.env_members = members

    def add_state_body(self, state_name, code):
        code = self.apply_keywords(code)
        if state_name in self.states:
            self.states[state_name].state_code = code

    def add_transition(self, from_name, to_name, guards):
        from_state = self.add_state(from_name)
        to_state = self.add_state(to_name)
        key = (from_name, to_name)
        if key in self.transitions:
            raise Exception('state transitions must be unique. '\
                    'Duplicate transitions found for state {} to state {}.'\
                    .format(from_name, to_name))
        guards = self.apply_keywords(guards)
        self.transitions[key] = guards
        self.states[from_name].add_transition(to_state, guards)

    @property
    def config(self):
        return SMGConfig(self.namer,
                         self.states.values(),
                         self.env_members)


class SMGConfigParser(object):
    def parse(self, txt):
        """Parse a configuration file"""
        builder = self.parse_header(txt)
        return self.parse_body(builder, txt).config

    def parse_header(self, txt):
        """Parse the configuration header from the configuration file
        Args:
            txt -- string to read a configuration Header from

        Look for configurations definitions between [[[smg]]] and [[[end]]] blocks
        """
        txt = find_config_text(txt, '[[[smg]]]', '[[[end]]]')
        txt = remove_indent(txt)
        dic = yaml.load(StringIO(txt))
        namer = SMGNamer(dic.get('prefix', 'smg'))
        b = SMGConfigBuilder(namer)
        for from_state, transitions in dic.get('states', {}).iteritems():
            b.add_state(from_state)
            if not transitions:
                continue
            for to_state, guards in transitions.iteritems():
                b.add_state(to_state)
                b.add_transition(from_state, to_state, guards)
        return b

    def parse_body(self, builder, txt):
        """Parse configuration body from the configuration file
        Args:
            txt -- string to read body definitions from

        Looks for body definitions of the following forms:

        // Declare environment struct members
        DECLARE_ENV {
            // C code defining struct members
            int a;
            int b;
            ...
        }

        // Define the body of a state function
        STATE_FN(state_name) {
            // C code executed when state_name is executed
            m->env.a += 1
            m->env.b -= 1
            ...
        }
        """
        keywords = {
            'DECLARE_ENV': lambda m, body: builder.add_env_members(body),
            kw_func('STATE_FN'): lambda m, body: builder.add_state_body(m.group(1), body),
        }
        for pattern, action in keywords.iteritems():
            for match in re.finditer(pattern, txt):
                body = ''.join(parse_pairs(txt[match.end():], '{', '}')).strip()
                if body:
                    action(match, body)
        return builder


def parse_pairs(iterable, open_delimiter, close_delimiter):
    """parse pairs of objects, e.g. paranetheses, brackets, ...
    """
    cnt = 0
    content_found = False
    for c in iterable:
        if not content_found and c == open_delimiter:
            cnt = 1
            content_found = True
            continue
        if cnt > 0:
            if c == close_delimiter:
                cnt -= 1
            elif c == open_delimiter:
                cnt += 1
        if content_found:
            if cnt > 0:
                yield c
            else:
                break
    if not content_found:
        raise SMGSyntaxError('malformed block')


def find_config_text(txt, start_delimiter, end_delimiter):
    """find a configuration block between the given delimiters
    """
    sidx = txt.find(start_delimiter)
    eidx = txt.find(end_delimiter)
    if sidx == -1:
        raise SMGConfigNotFound('unable to find start delimiter {!r}'\
                .format(start_delimiter))
    if eidx == -1:
        raise SMGConfigNotFound('unable to find end delimiter {!r}'\
                .format(end_delimiter))

    sidx += len(start_delimiter)

    if eidx < sidx:
        raise SMGConfigNotFound('end delimiter appears before start delimiter')
    return txt[sidx:eidx]


def find_indent(txt):
    """find the minimum index of the config"""
    idx = 0
    p = re.compile('\w')
    for line in txt.split('\n'):
        for m in p.finditer(line):
            idx = m.start()
            return idx
    return idx


def remove_indent(txt):
    """remove the indent from all lines"""
    out = []
    idx = find_indent(txt)
    for line in txt.split('\n'):
        out.append(line[idx:])
    return '\n'.join(out)
