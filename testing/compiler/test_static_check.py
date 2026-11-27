import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
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

    def test_literal_type_mismatch(self):
        self.assertTrue(errs(HEAD + 'int x = "abc"\nplot(x)\n'))
        self.assertTrue(errs(HEAD + 'int n = 1.5\nplot(n)\n'))
        self.assertTrue(errs(HEAD + 'bool b = 1\nplot(b ? 1 : 0)\n'))

    def test_literal_types_ok(self):
        self.assertEqual(errs(HEAD + 'float f = 1\nint i = 2\nstring s = "a"\nbool b = true\n'
                              'color c = #FF0000\nvar float v = 0.5\nplot(f + i + v, color = c)\n'), [])

    def test_conditional_ta_warning_t7(self):
        src = HEAD + 'float x = na\nif close > open\n    x := ta.ema(close, 10)\nplot(x)\n'
        warns = [f for f in psc.check(src, LEDGER) if f['severity'] == 'WARN']
        self.assertEqual([w['line'] for w in warns], [5])   # TradingView reported 5:10 for T7

    def test_ta_in_function_body_no_warning(self):
        src = HEAD + 'f(float s) =>\n    ta.sma(s, 3)\nplot(f(close))\n'
        self.assertEqual([f for f in psc.check(src, LEDGER) if f['severity'] == 'WARN'], [])


if __name__ == '__main__':
    unittest.main()
