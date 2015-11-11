import os
import unittest


class TestSMG(unittest.TestCase):
        """
        state_machine_members = [
            ('uint32_t', 'val'),
        ]
        sm = StateMachine('sm', state_machine_members)
        sm.states = (
            State(sm, 'start', '', (
                Transition(sm, 'off', 'true'),)),
            State(sm, 'on', '', (
                Transition(sm, 'off', 'true'),
                Transition(sm, 'rx', 'true'),
                Transition(sm, 'tx', 'true'))),
            State(sm, 'off', '', (
                Transition(sm, 'on', 'true'),
                Transition(sm, 'sleep', 'true'))),
            State(sm, 'sleep', '', (
                Transition(sm, 'off', 'true'),)),
            State(sm, 'reset', '', (
                Transition(sm, 'off', 'true'),)),
            State(sm, 'rx', '', (
                Transition(sm, 'on', 'true'),
                Transition(sm, 'tx', 'true'))),
            State(sm, 'tx', '', (
                Transition(sm, 'on', 'true'),
                Transition(sm, 'rx', 'true'))))

        sm.render(os.path.expanduser('~/Downloads/tmp/'))
        """
