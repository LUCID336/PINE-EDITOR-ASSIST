"""pinelab — local-first Pine Script v6 CLI (Pine Engineering Lab V5). No subscription, no network at run time.

Commands (JSON on stdout; --pretty for indentation):
  validate SCRIPT [--no-runtime] [--data CSV --base-tf TF --tf TF]
  run_indicator SCRIPT [--data CSV --base-tf TF --tf TF --inputs JSON --bars N]
  run_backtest SCRIPT [--data CSV --base-tf TF --tf TF --inputs JSON --oos 0.3 --cost-stress 2]
  get_capabilities
  export_txt SCRIPT --name NAME [--version NN]

Status vocabulary: LOCAL_VALIDATED | FAILED | BLOCKED (+ OK for run commands). TV_VERIFIED is never produced locally.
Exit codes: 0 ok/validated, 1 code errors/failed, 2 usage/data error, 3 blocked/unsupported, 4 timeout/resource limit.
Diagnostics use the TradingView MCP shape {message, start:{line,column}, end:{line,column}} plus code/stage/severity.
"""
import argparse
import json
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pinelab_core as core  # noqa: E402

LAB = core.LAB
RUNS = LAB / 'workspace' / 'runs'
COMPAT = LAB / 'compatibility.json'
SKILL_EXPORT = LAB / '.claude' / 'skills' / 'pine-script-engineering' / 'scripts' / 'export_txt.py'
UNSUPPORTED_LOCAL = None


def _compat():
    global UNSUPPORTED_LOCAL
    if UNSUPPORTED_LOCAL is None:
        try:
            ent = json.loads(COMPAT.read_text())['entries']
            UNSUPPORTED_LOCAL = {k.split(':', 1)[1].split('<')[0]: v['note'] for k, v in ent.items() if v['local'] == 'UNSUPPORTED'}
        except (OSError, ValueError, KeyError):
            UNSUPPORTED_LOCAL = {}
    return UNSUPPORTED_LOCAL


def envelope(command, **kw):
    e = {'tool': 'pinelab', 'lab_version': core.LAB_VERSION, 'command': command, 'backend': 'LOCAL',
         'engine': {'name': 'PineTS', 'version': core.engine_version(), 'adapter': 'pinelab-engine/1'},
         'status': None, 'errors': [], 'warnings': [], 'source_sha256': None, 'data_sha256': None,
         'duration_ms': None, 'result_ref': None, 'summary': {},
         'evidence_note': 'Local result. Not a TradingView compilation, runtime or backtest.'}
    e.update(kw)
    return e


def read_script(path, env):
    p = Path(path)
    if not p.is_file():
        env['errors'].append(core.diag(f'script not found: {path}', code='usage', stage='input'))
        return None
    if p.stat().st_size > core.LIMITS['script_max_bytes']:
        env['errors'].append(core.diag('script exceeds size limit', code='resource_limit', stage='input'))
        return None
    raw = p.read_bytes()
    try:
        src = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        env['errors'].append(core.diag('script is not valid UTF-8', code='encoding', stage='package'))
        return None
    env['source_sha256'] = core.sha256_file(p)
    return src


def check_data(path, env):
    p = Path(path or core.DEFAULT_DATA)
    if not p.is_file():
        env['errors'].append(core.diag(f'data file not found: {p}', code='data', stage='input'))
        return None
    if p.stat().st_size > core.LIMITS['csv_max_bytes']:
        env['errors'].append(core.diag('data file exceeds size limit', code='resource_limit', stage='input'))
        return None
    env['data_sha256'] = core.sha256_file(p)
    return p


def package_checks(src, env):
    lines = src.splitlines()
    if re.search(r'^\s*(```|~~~)', src, re.M):
        env['errors'].append(core.diag('Markdown fence in source', code='package', stage='package'))
    versions = [i + 1 for i, l in enumerate(lines) if re.match(r'^\s*//@version\s*=\s*\d+\s*$', l)]
    if len(versions) != 1:
        env['errors'].append(core.diag(f'expected exactly one //@version annotation, found {len(versions)}', 1, 1, 'package', 'package'))
    elif not re.match(r'^\s*//@version\s*=\s*6\s*$', lines[versions[0] - 1]):
        env['warnings'].append(core.diag('not Pine v6: local engine/ledger cover v6 only', versions[0], 1, 'version', 'package', 'warning'))
    if not re.search(r'^\s*(indicator|strategy|library)\s*\(', src, re.M):
        env['errors'].append(core.diag('missing indicator()/strategy()/library() declaration', code='declaration', stage='package'))


def static_stage(src, env):
    for f in core.static_check(src):
        sev = 'error' if f['severity'] == 'ERROR' else 'warning'
        (env['errors'] if sev == 'error' else env['warnings']).append(
            core.diag(f['message'], f['line'], f.get('column'), 'static_api', 'static', sev))


def capability_stage(src, env):
    """Flag constructs the local runtime cannot execute faithfully (BLOCKED instead of silent approximation)."""
    blockers = []
    code = core._psc.strip_code(src)
    for name, note in _compat().items():
        for m in re.finditer(r'(?<![\w.])' + re.escape(name) + r'(?![\w])', code):
            ln = code.count('\n', 0, m.start()) + 1
            blockers.append(core.diag(f'"{name}" is UNSUPPORTED locally: {note}', ln, m.start() - code.rfind('\n', 0, m.start()),
                                      'unsupported_local', 'capability', 'warning'))
            break
    if re.search(r'request\.security\s*\(', code) and re.search(r'^\S.*\bruntime\.error\s*\(|^\s*if\b[^\n]*\n\s+runtime\.error', code, re.M):
        env['warnings'].append(core.diag('global runtime.error combined with request.security: PineTS evaluates global code in the '
                                         'requested context and may raise it although TradingView does not (TV probes T3/T3b)',
                                         code='divergence_security_context', stage='capability', severity='warning'))
    if re.search(r'request\.footprint\s*\(', code):
        env['warnings'].append(core.diag('request.footprint returns na locally (no footprint data)', code='partial_local',
                                         stage='capability', severity='warning'))
    env['warnings'].extend(blockers)
    return blockers


def runtime_stage(script, args, env):
    data = check_data(args.data, env)
    if data is None:
        return None
    inputs = json.loads(args.inputs) if getattr(args, 'inputs', None) else None
    res = core.run_engine(script, csv=data, base_tf=args.base_tf, timeframe=args.tf, inputs=inputs, max_bars=getattr(args, 'bars', None))
    if not res.get('ok'):
        err = res.get('error', {})
        m = re.search(r'at (\d+):(\d+)', err.get('message', ''))
        env['errors'].append(core.diag(err.get('message', 'engine failed'), int(m.group(1)) if m else None,
                                       int(m.group(2)) if m else None, err.get('type', 'RUNTIME_ERROR').lower(), 'runtime'))
    for w in res.get('warnings') or []:
        env['warnings'].append(core.diag(str(w)[:300], code='engine_warning', stage='runtime', severity='warning'))
    return res


def reclassify_divergence(env):
    """A runtime error that matches a known local divergence is not evidence of a script bug -> BLOCKED."""
    if any(w.get('code') == 'divergence_security_context' for w in env['warnings']):
        rt = [e for e in env['errors'] if e.get('stage') == 'runtime' and e.get('code') == 'runtime_error']
        if rt and len(rt) == len(env['errors']):
            for e in rt:
                e['severity'] = 'warning'
                e['code'] = 'runtime_error_divergent'
                e['message'] += ' (raised locally only; known PineTS divergence, TradingView did not raise it in probe T3)'
                env['warnings'].append(e)
            env['errors'] = []
            return True
    return False


def save(env, payload, kind):
    RUNS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    p = RUNS / f"{stamp}_{kind}_{(env['source_sha256'] or 'na')[:10]}.json"
    p.write_text(json.dumps({'envelope': {k: v for k, v in env.items() if k != 'result_ref'}, 'result': payload}))
    env['result_ref'] = str(p.relative_to(LAB))


def exit_code(env):
    codes = {e.get('code') for e in env['errors']}
    if codes & {'timeout', 'resource_limit'}:
        return 4
    if env['status'] == 'BLOCKED':
        return 3
    if codes & {'usage', 'data', 'environment'}:
        return 2
    return 1 if env['errors'] or env['status'] == 'FAILED' else 0


# ---------------- commands ----------------
def cmd_validate(args):
    t0 = time.time()
    env = envelope('validate')
    src = read_script(args.script, env)
    if src is not None:
        package_checks(src, env)
        static_stage(src, env)
        blockers = capability_stage(src, env)
        runtime_ok = None
        if not args.no_runtime and not env['errors']:
            if blockers:
                env['summary']['runtime'] = 'SKIPPED (unsupported local features)'
            else:
                res = runtime_stage(args.script, args, env)
                runtime_ok = bool(res and res.get('ok'))
                if res and res.get('ok'):
                    env['summary']['runtime'] = {'bars': len(res.get('time') or []), 'plots': list(res['plots']),
                                                 'engine_ms': res.get('duration_ms')}
        divergent = reclassify_divergence(env)
        if env['errors']:
            env['status'] = 'FAILED'
        elif blockers or divergent:
            env['status'] = 'BLOCKED'
        else:
            env['status'] = 'LOCAL_VALIDATED'
        env['summary']['stages'] = {'package': 'run', 'static_api': 'run', 'capability': 'run',
                                    'runtime': 'skipped' if args.no_runtime or runtime_ok is None else ('ok' if runtime_ok else 'failed')}
    else:
        env['status'] = 'FAILED'
    env['duration_ms'] = int((time.time() - t0) * 1000)
    return env


def _series_summary(plots, time_):
    out = {}
    for k, v in plots.items():
        nums = [x for x in v if isinstance(x, (int, float)) and not isinstance(x, bool)]
        first = next((i for i, x in enumerate(v) if x is not None), None)
        out[k] = {'first_non_na_bar': first, 'na_count': sum(1 for x in v if x is None),
                  'last': v[-1] if v else None, 'min': min(nums) if nums else None, 'max': max(nums) if nums else None}
    return out


def cmd_run_indicator(args):
    t0 = time.time()
    env = envelope('run_indicator')
    src = read_script(args.script, env)
    if src is not None:
        package_checks(src, env)
        static_stage(src, env)
        blockers = capability_stage(src, env)
        if env['errors']:
            env['status'] = 'FAILED'
        elif blockers:
            env['status'] = 'BLOCKED'
        else:
            res = runtime_stage(args.script, args, env)
            if res and res.get('ok'):
                env['status'] = 'OK'
                env['summary'] = {'bars': len(res['time'] or []), 'first_bar_time_ms': (res['time'] or [None])[0],
                                  'last_bar_time_ms': (res['time'] or [None])[-1], 'timeframe': args.tf,
                                  'plots': _series_summary(res['plots'], res['time']), 'logs': len(res.get('logs') or []),
                                  'alerts': len(res.get('alerts') or [])}
                save(env, res, 'indicator')
            else:
                env['status'] = 'BLOCKED' if reclassify_divergence(env) else 'FAILED'
    else:
        env['status'] = 'FAILED'
    env['duration_ms'] = int((time.time() - t0) * 1000)
    return env


def _load_bars(csv_path, base_tf, tf, times):
    """Chart bars for the independent replay: same aggregation rule as LocalProvider (UTC grid), aligned to engine times."""
    import csv as _csv
    from collections import OrderedDict
    sys.path.insert(0, str(LAB / 'tools' / 'runtime'))
    ms = _tf_ms(tf)
    agg = OrderedDict()
    with open(csv_path) as f:
        for r in _csv.DictReader(f):
            t = int(float(r['time']))
            k = t - t % ms
            if k not in agg:
                agg[k] = dict(time=k, open=float(r['open']), high=float(r['high']), low=float(r['low']), close=float(r['close']))
            else:
                a = agg[k]
                a['high'] = max(a['high'], float(r['high'])); a['low'] = min(a['low'], float(r['low'])); a['close'] = float(r['close'])
    bars = list(agg.values())
    if [b['time'] for b in bars] != list(times):
        raise ValueError('bar alignment between engine and replay failed')
    return bars


def _tf_ms(tf):
    s = str(tf).upper()
    if s.isdigit():
        return int(s) * 60000
    m = re.fullmatch(r'(\d*)([DW])', s)
    if m:
        return int(m.group(1) or 1) * (86400000 if m.group(2) == 'D' else 7 * 86400000)
    raise ValueError(f'unsupported timeframe for replay: {tf}')


def cmd_run_backtest(args):
    t0 = time.time()
    env = envelope('run_backtest')
    src = read_script(args.script, env)
    if src is None:
        env['status'] = 'FAILED'
        return env
    package_checks(src, env)
    static_stage(src, env)
    blockers = capability_stage(src, env)
    params = core.strategy_params(src)
    if params is None:
        env['errors'].append(core.diag('not a strategy (no strategy() declaration)', code='not_a_strategy', stage='package'))
    if env['errors'] or blockers:
        env['status'] = 'FAILED' if env['errors'] else 'BLOCKED'
        env['duration_ms'] = int((time.time() - t0) * 1000)
        return env
    res = runtime_stage(args.script, args, env)
    if not (res and res.get('ok')):
        env['status'] = 'FAILED'
        env['duration_ms'] = int((time.time() - t0) * 1000)
        return env
    sys.path.insert(0, str(LAB / 'testing' / 'backtesting'))
    import backtester as bt
    s = res['strategy'] or {}
    engine_trades = [{'entry_bar': t['entry_bar_index'], 'entry_price': t['entry_price'], 'exit_bar': t.get('exit_bar_index'),
                      'exit_price': t.get('exit_price'), 'qty': t['size'], 'pnl': t.get('profit'), 'commission': t.get('commission')}
                     for t in s.get('closedtrades') or []]
    summary = {'engine_strategy': {'netprofit': s.get('netprofit'), 'closed_trades': len(engine_trades),
                                   'open_trades': len(s.get('opentrades') or []), 'max_drawdown': s.get('max_drawdown'),
                                   'config': {k: (s.get('config') or {}).get(k) for k in
                                              ['initial_capital', 'default_qty_type', 'default_qty_value', 'commission_type',
                                               'commission_value', 'slippage', 'process_orders_on_close', 'pyramiding']}}}
    plots = res['plots']
    if 'sig_entry_long' in plots and 'sig_exit_long' in plots:
        bars = _load_bars(args.data or core.DEFAULT_DATA, args.base_tf, args.tf, res['time'])
        cfg = s.get('config') or {}
        mintick = 0.0001  # LocalProvider symbol info
        p = bt.Params(initial_capital=float(cfg.get('initial_capital', params['initial_capital'])),
                      qty_type='percent_of_equity' if cfg.get('default_qty_type') == 'percent_of_equity' else 'fixed',
                      qty_value=float(cfg.get('default_qty_value', params['default_qty_value'])),
                      commission_pct=float(cfg.get('commission_value', 0)) if cfg.get('commission_type') == 'percent' else 0.0,
                      slippage_ticks=int(cfg.get('slippage', 0)), mintick=mintick,
                      process_orders_on_close=bool(cfg.get('process_orders_on_close', False)))
        if cfg.get('commission_type') not in (None, 'percent') and float(cfg.get('commission_value', 0)) != 0:
            env['warnings'].append(core.diag('replay models percent commission only', code='replay_limit', stage='backtest', severity='warning'))
        ent = [bool(x) for x in plots['sig_entry_long']]
        ext = [bool(x) for x in plots['sig_exit_long']]
        full = bt.run(bars, ent, ext, p)
        # parity: compare closed trades (replay force-closes at the end; engine keeps it open)
        replay_closed = [t for t in full.trades if not t.forced_exit]
        mism = []
        for a, b in zip(engine_trades, replay_closed):
            if a['entry_bar'] != b.entry_bar or a['exit_bar'] != b.exit_bar or abs(a['entry_price'] - b.entry_price) > 1e-6 \
                    or abs(a['exit_price'] - b.exit_price) > 1e-6 or abs((a['pnl'] or 0) - b.pnl) > 1e-6:
                mism.append({'engine': a, 'replay': {'entry_bar': b.entry_bar, 'entry_price': b.entry_price, 'exit_bar': b.exit_bar,
                                                     'exit_price': b.exit_price, 'pnl': b.pnl}})
        parity = {'engine_closed': len(engine_trades), 'replay_closed': len(replay_closed),
                  'trade_mismatches': len(mism) + abs(len(engine_trades) - len(replay_closed)), 'first_mismatches': mism[:3]}
        n = len(bars)
        cut = int(n * (1 - args.oos))
        is_r, oos_r = bt.run(bars, ent, ext, p, 0, cut), bt.run(bars, ent, ext, p, cut, n)
        stress_p = bt.Params(**{**p.__dict__, 'commission_pct': p.commission_pct * args.cost_stress,
                                'slippage_ticks': int(p.slippage_ticks * args.cost_stress)})
        stress = bt.run(bars, ent, ext, stress_p)
        summary.update({'independent_replay': {'model': 'testing/backtesting/backtester.py', 'params': full.params, 'metrics': full.metrics},
                        'parity_engine_vs_replay': parity,
                        'chronological_split': {'in_sample_bars': [0, cut], 'out_of_sample_bars': [cut, n],
                                                'in_sample': is_r.metrics, 'out_of_sample': oos_r.metrics,
                                                'note': 'Signals are computed on full history (indicator warm-up); trades are '
                                                        'only opened inside each segment and force-closed at its end.'},
                        'cost_stress': {'factor': args.cost_stress, 'metrics': stress.metrics}})
        status_ok = parity['trade_mismatches'] == 0
        if not status_ok:
            env['warnings'].append(core.diag(f"engine vs independent replay: {parity['trade_mismatches']} trade mismatches",
                                             code='parity', stage='backtest', severity='warning'))
    else:
        env['warnings'].append(core.diag('no sig_entry_long/sig_exit_long plots: independent replay, OOS split and cost stress NOT RUN',
                                         code='replay_not_run', stage='backtest', severity='warning'))
    env['summary'] = summary
    env['status'] = 'OK'
    save(env, {'engine': res.get('strategy'), 'summary': summary}, 'backtest')
    env['duration_ms'] = int((time.time() - t0) * 1000)
    return env


def cmd_get_capabilities(args):
    env = envelope('get_capabilities')
    comp = {}
    try:
        c = json.loads(COMPAT.read_text())
        comp = {'summary': c['summary'], 'generated': c['generated'], 'reference_snapshot': c['reference_snapshot'],
                'other_versions': c['other_versions']}
    except (OSError, ValueError, KeyError):
        env['warnings'].append(core.diag('compatibility.json missing: run tools/build_compatibility.py', code='environment', severity='warning'))
    env['summary'] = {
        'environment': {'python': platform.python_version(), 'node': core.node_version(), 'os': platform.system()},
        'engine_installed': core.engine_version() is not None,
        'ledger': json.loads((LAB / 'knowledge/reference/v6-api-ledger.json').read_text())['meta']['counts'],
        'compatibility': comp,
        'datasets': sorted(str(p.relative_to(LAB)) for p in (LAB / 'testing' / 'synthetic_data').glob('*.csv')),
        'limits': core.LIMITS,
        'commands': ['validate', 'run_indicator', 'run_backtest', 'get_capabilities', 'export_txt'],
        'not_available_locally': ['TradingView compile (TV_VERIFIED needs the official editor or MCP)', 'realtime ticks/rollback',
                                  'sessions/holidays/DST in data', 'fundamental/economic data', 'footprint data', 'aggressor_side'],
        'cost': 'No paid service, API key or subscription required for the local core.'}
    env['status'] = 'OK' if core.engine_version() and core.node_version() else 'BLOCKED'
    return env


def cmd_export_txt(args):
    t0 = time.time()
    env = cmd_validate(argparse.Namespace(script=args.script, no_runtime=args.no_runtime, data=None, base_tf=core.DEFAULT_BASE_TF, tf='60'))
    env['command'] = 'export_txt'
    if env['status'] == 'FAILED':
        env['errors'].append(core.diag('export refused: validation FAILED', code='export_refused', stage='export'))
        return env
    safe = re.sub(r'[^A-Za-z0-9_]+', '_', args.name).strip('_').lower()
    dest = LAB / 'releases' / 'txt' / f'{safe}_v{int(args.version):02d}.txt'
    if dest.exists():
        env['errors'].append(core.diag(f'{dest.relative_to(LAB)} exists; bump --version (no overwrite)', code='export_exists', stage='export'))
        env['status'] = 'FAILED'
        return env
    p = subprocess.run([sys.executable, str(SKILL_EXPORT), args.script, str(dest)], capture_output=True, text=True)
    if p.returncode != 0:
        env['errors'].append(core.diag((p.stderr or p.stdout).strip().splitlines()[-1], code='export_failed', stage='export'))
        env['status'] = 'FAILED'
    else:
        env['result_ref'] = str(dest.relative_to(LAB))
        env['summary']['txt'] = {'path': env['result_ref'], 'sha256': core.sha256_file(dest), 'bytes': dest.stat().st_size,
                                 'validation_status': env['status']}
    env['duration_ms'] = int((time.time() - t0) * 1000)
    return env


def main(argv=None):
    ap = argparse.ArgumentParser(prog='pinelab', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pretty', action='store_true')
    sub = ap.add_subparsers(dest='cmd', required=True)

    def data_args(p):
        p.add_argument('--data', default=None, help='CSV time,open,high,low,close,volume (UTC ms)')
        p.add_argument('--base-tf', default=core.DEFAULT_BASE_TF, help='timeframe of the CSV rows (e.g. 15, 60, D)')
        p.add_argument('--tf', default='60', help='chart timeframe (>= base)')
        p.add_argument('--inputs', default=None, help='JSON {input title: value}')
    v = sub.add_parser('validate'); v.add_argument('script'); v.add_argument('--no-runtime', action='store_true'); data_args(v)
    r = sub.add_parser('run_indicator'); r.add_argument('script'); data_args(r); r.add_argument('--bars', type=int, default=None)
    b = sub.add_parser('run_backtest'); b.add_argument('script'); data_args(b)
    b.add_argument('--oos', type=float, default=0.3, help='out-of-sample fraction (chronological tail)')
    b.add_argument('--cost-stress', type=float, default=2.0)
    sub.add_parser('get_capabilities')
    e = sub.add_parser('export_txt'); e.add_argument('script'); e.add_argument('--name', required=True)
    e.add_argument('--version', default=1); e.add_argument('--no-runtime', action='store_true')
    a = ap.parse_args(argv)
    fn = {'validate': cmd_validate, 'run_indicator': cmd_run_indicator, 'run_backtest': cmd_run_backtest,
          'get_capabilities': cmd_get_capabilities, 'export_txt': cmd_export_txt}[a.cmd]
    try:
        env = fn(a)
    except Exception as ex:  # never report success on an internal failure
        env = envelope(a.cmd, status='FAILED', errors=[core.diag(f'internal error: {type(ex).__name__}: {ex}', code='internal')])
    print(json.dumps(env, indent=1 if a.pretty else None, default=str))
    return exit_code(env)


if __name__ == '__main__':
    sys.exit(main())
