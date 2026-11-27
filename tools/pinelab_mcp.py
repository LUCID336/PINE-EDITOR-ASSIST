"""Optional local MCP wrapper (stdio, JSON-RPC 2.0) around pinelab. No network, no secrets, no paid endpoint.

Exposes: validate, run_indicator, run_backtest, get_capabilities, export_txt. Each tool returns the same JSON
envelope as the CLI. Registered in .mcp.json; the CLI remains the primary, stable interface.
"""
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pinelab  # noqa: E402
import pinelab_core as core  # noqa: E402

PROTOCOL = '2025-06-18'
DATA_PROPS = {'data': {'type': 'string', 'description': 'CSV path (time,open,high,low,close,volume; UTC ms). Default: bundled synthetic data'},
              'base_tf': {'type': 'string', 'default': core.DEFAULT_BASE_TF}, 'tf': {'type': 'string', 'default': '60'},
              'inputs': {'type': 'object', 'description': 'Input overrides by input title'}}
TOOLS = [
    {'name': 'validate', 'description': 'Validate a Pine v6 script locally (package, static API vs official ledger, capability, PineTS runtime). '
                                        'Returns LOCAL_VALIDATED / FAILED / BLOCKED. Not a TradingView compile.',
     'inputSchema': {'type': 'object', 'required': ['script'], 'properties': {'script': {'type': 'string'}, 'no_runtime': {'type': 'boolean'}, **DATA_PROPS}}},
    {'name': 'run_indicator', 'description': 'Run a Pine indicator locally on CSV data; returns plot summaries and a result file reference.',
     'inputSchema': {'type': 'object', 'required': ['script'], 'properties': {'script': {'type': 'string'}, 'bars': {'type': 'integer'}, **DATA_PROPS}}},
    {'name': 'run_backtest', 'description': 'Backtest a Pine strategy locally: PineTS emulator + independent Python replay, OOS split, cost stress, evidence flags.',
     'inputSchema': {'type': 'object', 'required': ['script'], 'properties': {'script': {'type': 'string'}, 'oos': {'type': 'number', 'default': 0.3},
                                                                               'cost_stress': {'type': 'number', 'default': 2.0}, **DATA_PROPS}}},
    {'name': 'get_capabilities', 'description': 'Local environment, engine version, compatibility summary, limits.',
     'inputSchema': {'type': 'object', 'properties': {}}},
    {'name': 'export_txt', 'description': 'Validate and export complete Pine source to releases/txt/<name>_vNN.txt (no overwrite).',
     'inputSchema': {'type': 'object', 'required': ['script', 'name'], 'properties': {'script': {'type': 'string'}, 'name': {'type': 'string'},
                                                                                       'version': {'type': 'integer', 'default': 1}}}},
]


def call(name, a):
    ns = argparse.Namespace(script=a.get('script'), data=a.get('data'), base_tf=a.get('base_tf', core.DEFAULT_BASE_TF), tf=a.get('tf', '60'),
                            inputs=json.dumps(a['inputs']) if a.get('inputs') else None, no_runtime=bool(a.get('no_runtime')),
                            bars=a.get('bars'), oos=float(a.get('oos', 0.3)), cost_stress=float(a.get('cost_stress', 2.0)),
                            name=a.get('name'), version=a.get('version', 1))
    fn = {'validate': pinelab.cmd_validate, 'run_indicator': pinelab.cmd_run_indicator, 'run_backtest': pinelab.cmd_run_backtest,
          'get_capabilities': pinelab.cmd_get_capabilities, 'export_txt': pinelab.cmd_export_txt}[name]
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(ns)


def handle(msg):
    mid, method, params = msg.get('id'), msg.get('method'), msg.get('params') or {}
    if method == 'initialize':
        return {'jsonrpc': '2.0', 'id': mid, 'result': {'protocolVersion': params.get('protocolVersion', PROTOCOL),
                                                        'capabilities': {'tools': {}},
                                                        'serverInfo': {'name': 'pinelab', 'version': core.LAB_VERSION}}}
    if method == 'tools/list':
        return {'jsonrpc': '2.0', 'id': mid, 'result': {'tools': TOOLS}}
    if method == 'tools/call':
        name = params.get('name')
        if name not in {t['name'] for t in TOOLS}:
            return {'jsonrpc': '2.0', 'id': mid, 'error': {'code': -32602, 'message': f'unknown tool {name}'}}
        try:
            env = call(name, params.get('arguments') or {})
            failed = env.get('status') in ('FAILED',)
            return {'jsonrpc': '2.0', 'id': mid, 'result': {'content': [{'type': 'text', 'text': json.dumps(env, default=str)}],
                                                            'structuredContent': env, 'isError': failed}}
        except Exception as ex:  # report, never fake success
            return {'jsonrpc': '2.0', 'id': mid, 'result': {'content': [{'type': 'text', 'text': f'internal error: {ex}'}], 'isError': True}}
    if method == 'ping':
        return {'jsonrpc': '2.0', 'id': mid, 'result': {}}
    if mid is None:      # notification (e.g. notifications/initialized)
        return None
    return {'jsonrpc': '2.0', 'id': mid, 'error': {'code': -32601, 'message': f'method not found: {method}'}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except json.JSONDecodeError:
            resp = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'parse error'}}
        if resp is not None:
            sys.stdout.write(json.dumps(resp, default=str) + '\n')
            sys.stdout.flush()


if __name__ == '__main__':
    main()
