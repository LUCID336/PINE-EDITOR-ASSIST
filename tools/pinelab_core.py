"""Shared core of the Pine Engineering Lab V5 (used by tools/pinelab.py, the MCP wrapper and the test suites).

Backends: LOCAL only (PineTS via tools/runtime/engine.mjs + static checker). No network, no paid services.
Every result states engine + version, source/data SHA-256 and duration. Local results are never TradingView evidence.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
TOOLS = LAB / 'tools'
RUNTIME = TOOLS / 'runtime'
DEFAULT_DATA = LAB / 'testing' / 'synthetic_data' / 'synth_15m_seed7.csv'
DEFAULT_BASE_TF = '15'
LAB_VERSION = '5.0.0'

LIMITS = {
    'script_max_bytes': 512 * 1024,
    'csv_max_bytes': 200 * 1024 * 1024,
    'timeout_s': 60,
    'node_heap_mb': 1024,
    'cpu_seconds': 120,
    'max_loops': 100000,
}

sys.path.insert(0, str(TOOLS))
import pine_static_check as _psc  # noqa: E402

_LEDGER = None


def ledger():
    global _LEDGER
    if _LEDGER is None:
        _LEDGER = _psc.load_ledger()
    return _LEDGER


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def diag(message, line=None, column=None, code=None, stage=None, severity='error'):
    """Diagnostic in the TradingView MCP shape: {message, start:{line,column}, end:{line,column}} + lab fields."""
    pos = {'line': line, 'column': column} if line else None
    return {'message': message, 'start': pos, 'end': pos, 'code': code, 'stage': stage, 'severity': severity}


def node_version():
    try:
        return subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def engine_version():
    try:
        return json.loads((RUNTIME / 'node_modules' / 'pinets' / 'package.json').read_text())['version']
    except (OSError, ValueError, KeyError):
        return None


def _preexec():  # POSIX only: CPU-time limit for the engine process
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (LIMITS['cpu_seconds'], LIMITS['cpu_seconds'] + 5))
    except (ImportError, ValueError, OSError):
        pass


def run_engine(script, csv=None, base_tf=None, timeframe='60', symbol='LOCAL:SYNTH', inputs=None,
               max_bars=None, timeout_s=None):
    """Run a Pine script in PineTS on a local CSV. Returns the engine response dict (+ 'process' metadata).
    Raises nothing for script problems; they come back as ok=False with error.type."""
    csv = Path(csv or DEFAULT_DATA)
    req = {'script': str(Path(script).resolve()), 'csv': str(csv.resolve()), 'base_timeframe': str(base_tf or DEFAULT_BASE_TF),
           'timeframe': str(timeframe), 'symbol': symbol, 'inputs': inputs, 'max_bars': max_bars, 'max_loops': LIMITS['max_loops']}
    with tempfile.TemporaryDirectory(prefix='pinelab-') as td:
        rq, rs = Path(td, 'req.json'), Path(td, 'res.json')
        rq.write_text(json.dumps(req))
        cmd = ['node', f"--max-old-space-size={LIMITS['node_heap_mb']}", str(RUNTIME / 'engine.mjs'), str(rq), str(rs)]
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=RUNTIME, capture_output=True, text=True, timeout=timeout_s or LIMITS['timeout_s'],
                                  preexec_fn=_preexec if os.name == 'posix' else None)
        except subprocess.TimeoutExpired:
            return {'ok': False, 'error': {'type': 'TIMEOUT', 'message': f"engine exceeded {timeout_s or LIMITS['timeout_s']} s"},
                    'duration_ms': int((time.time() - t0) * 1000)}
        except FileNotFoundError:
            return {'ok': False, 'error': {'type': 'ENVIRONMENT', 'message': 'node not found on PATH (install Node.js >= 20)'}}
        if not rs.exists():
            msg = (proc.stderr or proc.stdout or '').strip().splitlines()
            kind = 'RESOURCE_LIMIT' if proc.returncode in (-9, -24, 134, 137) or 'heap' in (proc.stderr or '').lower() else 'ENGINE_CRASH'
            return {'ok': False, 'error': {'type': kind, 'message': (msg[-1] if msg else f'exit {proc.returncode}')[:500]},
                    'duration_ms': int((time.time() - t0) * 1000)}
        res = json.loads(rs.read_text())
        res['process'] = {'returncode': proc.returncode, 'wall_ms': int((time.time() - t0) * 1000)}
        return res


def static_check(source):
    return _psc.check(source, ledger())


def strategy_params(source):
    """Read cost/size parameters from the strategy() declaration (literal values only)."""
    import re
    m = re.search(r'^\s*strategy\s*\((.*?)\)\s*$', source, re.M | re.S)
    params = {'initial_capital': 1000000.0, 'default_qty_type': 'strategy.fixed', 'default_qty_value': 1.0,
              'commission_type': 'strategy.commission.percent', 'commission_value': 0.0, 'slippage': 0,
              'process_orders_on_close': False, 'pyramiding': 1}  # TradingView documented defaults
    if not m:
        return None
    for k in params:
        mm = re.search(rf'\b{k}\s*=\s*([\w.]+)', m.group(1))
        if mm:
            v = mm.group(1)
            params[k] = (v == 'true') if v in ('true', 'false') else (float(v) if re.fullmatch(r'-?\d+(\.\d+)?', v) else v)
    return params
