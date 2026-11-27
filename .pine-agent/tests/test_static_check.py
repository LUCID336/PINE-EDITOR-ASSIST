import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import pine_static_check as psc  # noqa: E402

LEDGER = psc.load_ledger()
HEAD = '//@version=6\nindicator("t", overlay = true)\n'


def errs(src):
    return [f for f in psc.check(src, LEDGER) if f['severity'] == 'ERROR']


class StaticCheckTests(unittest.TestCase):
    def test_clean_script(self):
        src = HEAD + ('float htf = request.security(syminfo.tickerid, "D", close[1], '
                      'lookahead = barmerge.lookahead_on)\nplot(ta.ema(close, 20), color = color.new(color.blue, 0))\n')
        self.assertEqual(errs(src), [])

    def test_fabricated_function(self):
        self.assertTrue(errs(HEAD + 'plot(ta.superema(close, 20))\n'))

    def test_unknown_global_function(self):
        self.assertTrue(errs(HEAD + 'plot(smooth(close))\n'))

    def test_user_function_ok(self):
        self.assertEqual(errs(HEAD + 'smooth(float s) =>\n    ta.sma(s, 3)\nplot(smooth(close))\n'), [])

    def test_wrong_named_argument(self):
        self.assertTrue(errs(HEAD + 'plot(close, linewidth2 = 2)\n'))

    def test_unknown_variable(self):
        self.assertTrue(errs(HEAD + 'plot(barstate.isclosed ? close : na)\n'))

    def test_new_2026_variable_known(self):
        self.assertEqual(errs(HEAD + 'plot(aggressor_side == aggressor.buy ? 1 : 0)\n'), [])

    def test_transp_removed(self):
        self.assertTrue(errs(HEAD + 'bgcolor(color.red, transp = 80)\n'))

    def test_pre_v5_calls(self):
        self.assertTrue(errs('//@version=6\nstudy("x")\nplot(security(syminfo.tickerid, "D", close))\n'))

    def test_version_annotation(self):
        self.assertTrue(errs('indicator("x")\nplot(close)\n'))

    def test_strings_and_comments_ignored(self):
        self.assertEqual(errs(HEAD + '// ta.fake(close)\nlabel.new(bar_index, high, "ta.fake(x)")\n'
                              's = """ta.fake2(\n"""\n'), [])

    def test_udt_and_methods(self):
        src = HEAD + ('type Pt\n    float price\n    int t\nmethod add(array<Pt> a, float p) =>\n'
                      '    a.push(Pt.new(p, time))\nvar pts = array.new<Pt>()\npts.add(close)\n'
                      'pts.sort(order.ascending, sort_field = "price")\n')
        self.assertEqual(errs(src), [])


if __name__ == '__main__':
    unittest.main()
