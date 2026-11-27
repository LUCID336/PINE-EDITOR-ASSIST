"""Build compatibility.json: per official v6 API entry, local (PineTS + LocalProvider) status and TradingView evidence.

Local status vocabulary (V5 contract):
  SUPPORTED_TESTED  numerically compared with an independent reference in testing/ (evidence path given)
  PARTIAL           works locally with documented limits or known divergence
  UNSUPPORTED       absent in PineTS, refused locally, or no local data source
  UNVERIFIED        present in PineTS (function probe) or a plain variable/constant, but not tested
TradingView status: TV_VERIFIED_RELAYED (user-operated AI Copilot, see testing/regression/tv_probes/) or NOT_TESTED.
Usage: python tools/build_compatibility.py [--probe PROBE.json]   (runs tools/runtime/probe_functions.mjs if omitted)
"""
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
REF = 'testing/regression/test_indicator_reference.py'
BT = 'testing/backtesting/test_strategy_parity.py'
TV = 'testing/regression/tv_probes/TV_RESULTS_2026-11-27.md'

TESTED = {  # name -> evidence
    **{n: REF for n in ['ta.sma', 'ta.ema', 'ta.rma', 'ta.rsi', 'ta.atr', 'ta.tr', 'ta.highest', 'ta.lowest', 'ta.stdev',
                        'ta.change', 'ta.cum', 'ta.crossover', 'ta.crossunder', 'ta.pivothigh', 'ta.pivotlow',
                        'array.new', 'array.push', 'array.shift', 'array.size', 'array.avg', 'array.get', 'array.last',
                        'request.security_lower_tf', 'plot', 'indicator', 'input.int', 'input.bool', 'input.float', 'math.max']},
    **{n: BT for n in ['strategy', 'strategy.entry', 'strategy.close']},
    **{n: REF for n in ['close', 'open', 'high', 'low', 'volume', 'time', 'bar_index', 'barmerge.lookahead_on']},
}
PARTIAL = {
    'request.security': 'Tested vs independent aggregation on 24/7 UTC calendar grid (D, 240; lookahead on/off historical). '
                        'Divergence: PineTS re-executes the whole script in the requested context (global runtime.error fires '
                        'locally, not on TradingView - TV probes T3/T3b). Sessions, holidays, DST, realtime NOT modelled.',
    'strategy': 'PineTS broker emulator: next-bar-open fills and percent commission match TradingView (T9) and the independent '
                'Python model; slippage, percent_of_equity sizing, margin, intrabar/bar detalization NOT TradingView-verified.',
    'strategy.entry': 'see strategy', 'strategy.close': 'see strategy',
    'ta.pivothigh': 'Values/timing tested; tie rule locally = (>= left, > right); TradingView tie side UNVERIFIED (probe T11).',
    'ta.pivotlow': 'Values/timing tested; tie rule not tested.',
    'request.footprint': 'Returns na locally: LocalProvider has no footprint data (PineTS needs a provider footprint surface).',
    'log.info': 'Captured to engine logs; formatting not compared with TradingView.',
    'alert': 'Collected in engine output; delivery/frequency semantics not modelled.',
    'runtime.error': 'Raised locally; see request.security divergence for global guards.',
    'barstate.isconfirmed': 'Historical bars only (always true); realtime ticks/rollback not available locally.',
    'barstate.isrealtime': 'No realtime bars locally (always false).',
    'syminfo.tickerid': 'Synthetic symbol info from LocalProvider.',
    'timeframe.in_seconds': 'Context-dependent value matches TradingView inside request.security (T3b).',
}
UNSUPPORTED = {
    'aggressor_side': 'PineTS 0.13.1: Undeclared identifier (TradingView compiles it, T5).',
    'aggressor.buy': 'Depends on aggressor_side support.', 'aggressor.sell': 'Depends on aggressor_side support.',
    **{n: 'No local data source (fundamental/economic/external data).' for n in [
        'request.financial', 'request.economic', 'request.earnings', 'request.dividends', 'request.splits',
        'request.quandl', 'request.seed', 'request.currency_rate']},
}
TV_VERIFIED = {
    'ta.ema': 'T1 warm-up (first non-na bar = length-1)', 'ta.rsi': 'T2 constant series = 100',
    'request.security': 'T3/T3b/T6/T6b context + HTF idiom semantics', 'timeframe.in_seconds': 'T3b',
    'ta.pivothigh': 'T10 timing/value', 'strategy.entry': 'T9 fills', 'strategy.close': 'T9 fills',
    'strategy': 'T9 commission', 'barstate.isclosed': 'T8c: does NOT exist (compile error)',
    'plot': 'T8a named-argument error text', 'aggressor_side': 'T5 compiles', 'calc_on_every_history_tick': 'T5 compiles',
}


def main():
    probe = None
    if '--probe' in sys.argv:
        probe = json.loads(Path(sys.argv[sys.argv.index('--probe') + 1]).read_text())
    else:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td, 'probe.json')
            subprocess.run(['node', 'probe_functions.mjs', str(LAB / 'knowledge/reference/v6-api-ledger.json'), str(out)],
                           cwd=LAB / 'tools/runtime', check=True, capture_output=True, timeout=300)
            probe = json.loads(out.read_text())
    ledger = json.loads((LAB / 'knowledge/reference/v6-api-ledger.json').read_text())
    entries, counts = {}, {}
    for e in ledger['entries']:
        name = e['name'].split('<')[0]
        if name in UNSUPPORTED:
            st, note, ev = 'UNSUPPORTED', UNSUPPORTED[name], None
        elif e['kind'] == 'fun' and probe.get(e['name']) == 'ABSENT':
            st, note, ev = 'UNSUPPORTED', 'Absent in PineTS (function probe).', 'tools/runtime/probe_functions.mjs'
        elif name in PARTIAL:
            st, note, ev = 'PARTIAL', PARTIAL[name], TESTED.get(name)
        elif name in TESTED:
            st, note, ev = 'SUPPORTED_TESTED', 'Matches independent reference (values + warm-up).', TESTED[name]
        else:
            st, note, ev = 'UNVERIFIED', ('Present in PineTS (function probe), not tested.' if e['kind'] == 'fun'
                                          else 'Not tested locally.'), None
        key = f"{e['kind']}:{e['name']}"
        entries[key] = {'local': st, 'note': note, 'evidence': ev,
                        'tradingview': 'TV_VERIFIED_RELAYED' if name in TV_VERIFIED else 'NOT_TESTED',
                        'tradingview_evidence': (TV + ' ' + TV_VERIFIED[name]) if name in TV_VERIFIED else None}
        counts[st] = counts.get(st, 0) + 1
    out = {'schema': 'pinelab-compatibility/1', 'generated': date.today().isoformat(), 'pine_version': 'v6',
           'engine': {'name': 'PineTS', 'version': json.loads((LAB / 'tools/runtime/node_modules/pinets/package.json').read_text())['version']},
           'reference_snapshot': ledger['meta']['retrieved'], 'summary': counts,
           'other_versions': {'v5': 'UNVERIFIED locally (PineTS documents v5 transpilation; not tested). Use V3 migration sheet M73.',
                              'v1-v4': 'Not executable locally; use V3 migration modules M74-M76 and the official migration guides.'},
           'status_rule': 'LOCAL statuses never imply TradingView parity; only TV_VERIFIED* columns carry TradingView evidence.',
           'entries': entries}
    (LAB / 'compatibility.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print('compatibility.json', counts)


if __name__ == '__main__':
    main()
