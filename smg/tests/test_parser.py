import unittest
from smg.parser import parse_pairs, find_indent, remove_indent, SMGConfigParser

class TestPairParser(unittest.TestCase):
    def test_simple(self):
        self.assertEqual('abcd', ''.join(parse_pairs('(abcd)', '(', ')')))
        self.assertEqual('abcd', ''.join(parse_pairs('[abcd]', '[', ']')))

    def test_nested(self):
        self.assertEqual('(a)((b)c)d', ''.join(parse_pairs('((a)((b)c)d)', '(', ')')))


class TestRemoveIndent(unittest.TestCase):
    def test_no_indent(self):
        txt = "a\n b\n  d\n   e\n"
        self.assertEqual(0, find_indent(txt))
        self.assertEqual(txt, remove_indent(txt))

    def test_indent(self):
        txt = "***a\n****b\n**** c\n"
        self.assertEqual(3, find_indent(txt))
        self.assertEqual("a\n*b\n* c\n", remove_indent(txt))


cfg = """\
/**
 * Some comments here
 *
 * [[[smg]]]
 * prefix: smg_garage
 *
 * states:
 *  init:
 *
 * [[[end]]]
 */

DECLARE_ENV {
    int a;
    int b;
}

STATE_FN(init) {
    ENV.a += 1;
    ENV.b += 2;
}
"""


class TestConfigParser(unittest.TestCase):
    def test_read_config(self):
        parser = SMGConfigParser()
        print(parser.parse(cfg))
