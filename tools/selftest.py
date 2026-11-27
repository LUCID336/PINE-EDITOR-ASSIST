"""Offline self-test of the Pine Engineering Lab V5 (run after installation).

All network access is blocked for the child processes (proxy variables point to a closed local port, npm offline),
so a PASS proves the local core needs no internet, no TradingView login and no paid service.
Usage: python tools/selftest.py [--quick] [--json OUT]
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
BLOCKED = {'HTTP_PROXY': 'http://127.0.0.1:9', 'HTTPS_PROXY': 'http://127.0.0.1:9', 'http_proxy': 'http://127.0.0.1:9',
           'https_proxy': 'http://127.0.0.1:9', 'ALL_PROXY': 'http://127.0.0.1:9', 'NO_PROXY': '', 'no_proxy': '',
           'npm_config_offline': 'true', 'PYTHONDONTWRITEBYTECODE': '1'}


def step(name, cmd, expect_rc=0, check=None):
    env = {**os.environ, **BLOCKED}
    t0 = time.time()
    p = subprocess.run(cmd, cwd=LAB, capture_output=True, text=True, env=env, timeout=900)
    ok = p.returncode == expect_rc
    detail = ''
    if ok and check:
        ok, detail = check(p.stdout)
    tail = (p.stdout.strip().splitlines() or [''])[-1][:160]
    return {'step': name, 'status': 'PASS' if ok else 'FAIL', 'returncode': p.returncode, 'seconds': round(time.time() - t0, 1),
            'detail': detail or tail, 'stderr_tail': (p.stderr.strip().splitlines() or [''])[-1][:200] if not ok else ''}


def jcheck(pred, what):
    def f(out):
        try:
            e = json.loads(out)
        except ValueError:
            return False, 'no JSON'
        return pred(e), what + ': ' + str(e.get('status'))
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true', help='skip the slower pytest suites')
    ap.add_argument('--json')
    a = ap.parse_args()
    py = sys.executable
    pl = [py, 'tools/pinelab.py']
    steps = [
        step('capabilities', pl + ['get_capabilities'], 0, jcheck(lambda e: e['summary']['engine_installed'], 'engine')),
        step('validate good script', pl + ['validate', 'releases/txt/academy_L01_sma_change_v01.txt'], 0,
             jcheck(lambda e: e['status'] == 'LOCAL_VALIDATED', 'status')),
        step('validate syntax error -> FAILED', pl + ['validate', 'testing/regression/fixtures/syntax_error.pine'], 1,
             jcheck(lambda e: e['status'] == 'FAILED' and e['errors'], 'status')),
        step('validate unknown function -> FAILED', pl + ['validate', 'testing/regression/fixtures/missing_function.pine'], 1,
             jcheck(lambda e: e['status'] == 'FAILED' and e['errors'][0]['start'], 'status')),
        step('invalid input (missing data) -> usage error', pl + ['run_indicator', 'releases/txt/academy_L01_sma_change_v01.txt',
                                                                  '--data', 'does_not_exist.csv'], 2,
             jcheck(lambda e: e['status'] == 'FAILED', 'status')),
        step('unsupported feature -> BLOCKED', pl + ['validate', 'testing/regression/tv_probes/T5_features_2026.pine'], 3,
             jcheck(lambda e: e['status'] == 'BLOCKED', 'status')),
        step('EMA indicator on local OHLCV', pl + ['run_indicator', 'testing/regression/fixtures/ema_poc.pine'], 0,
             jcheck(lambda e: e['status'] == 'OK' and e['summary']['plots']['ema20']['first_non_na_bar'] == 19, 'status')),
        step('backtest with parity', pl + ['run_backtest', 'workspace/strategies/ema_trend_longflat_v1.pine', '--data',
                                           'testing/synthetic_data/synth_60m_seed11.csv', '--base-tf', '60', '--tf', '60'], 0,
             jcheck(lambda e: e['summary']['parity_engine_vs_replay']['trade_mismatches'] == 0, 'parity')),
        step('static checker unit tests', [py, '-m', 'unittest', 'discover', '-s', 'testing/compiler'], 0),
    ]
    steps = [s for s in steps if s]
    kb = LAB / '.claude' / 'skills' / 'pine-script-engineering' / 'knowledge' / 'PINE_AGENT'
    if kb.exists():
        env = {**os.environ, **BLOCKED}
        p = subprocess.run([py, '-m', 'unittest', 'discover', '-s', 'tests'], cwd=kb, capture_output=True, text=True, env=env)
        steps.append({'step': 'V3/V4 knowledge base tests', 'status': 'PASS' if p.returncode == 0 else 'FAIL',
                      'returncode': p.returncode, 'detail': (p.stderr.strip().splitlines() or [''])[-1]})
    if not a.quick:
        steps.append(step('pytest suites (reference, contract, backtest)', [py, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'testing'], 0))
    ok = all(s['status'] == 'PASS' for s in steps)
    report = {'selftest': 'PASS' if ok else 'FAIL', 'network': 'blocked via proxy 127.0.0.1:9 + npm offline', 'steps': steps,
              'note': 'LOCAL evidence only; no TradingView compilation involved.'}
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=1))
    for s in steps:
        print(f"{s['status']:4}  {s['step']}  ({s.get('detail', '')})")
    print('SELFTEST', report['selftest'])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
