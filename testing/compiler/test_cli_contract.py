"""Phase 02 contract: explicit errors instead of success, timeout and resource limits, JSON envelope fields."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / 'tools'))
import pinelab_core as core  # noqa: E402

CLI = [sys.executable, str(LAB / 'tools' / 'pinelab.py')]


def cli(*args):
    p = subprocess.run(CLI + list(args), cwd=LAB, capture_output=True, text=True, timeout=300)
    return p.returncode, json.loads(p.stdout)


def test_envelope_fields():
    rc, e = cli('validate', 'releases/txt/academy_L01_sma_change_v01.txt')
    assert rc == 0 and e['status'] == 'LOCAL_VALIDATED'
    for k in ['tool', 'lab_version', 'engine', 'status', 'errors', 'warnings', 'source_sha256', 'data_sha256', 'duration_ms', 'evidence_note']:
        assert k in e
    assert e['engine']['version'] and len(e['source_sha256']) == 64 and len(e['data_sha256']) == 64


@pytest.mark.parametrize('fixture,code', [('syntax_error.pine', 1), ('missing_function.pine', 1)])
def test_errors_are_explicit(fixture, code):
    rc, e = cli('validate', f'testing/regression/fixtures/{fixture}')
    assert rc == code and e['status'] == 'FAILED' and e['errors']


def test_invalid_input_is_usage_error():
    rc, e = cli('run_indicator', 'releases/txt/academy_L01_sma_change_v01.txt', '--data', 'nope.csv')
    assert rc == 2 and e['errors'][0]['code'] == 'data'


def test_unsupported_is_blocked_not_success():
    rc, e = cli('validate', 'testing/regression/tv_probes/T5_features_2026.pine')
    assert rc == 3 and e['status'] == 'BLOCKED'


def test_timeout_is_reported(tmp_path):
    s = tmp_path / 'slow.pine'
    s.write_text('//@version=6\nindicator("slow")\nfloat acc = 0.0\nfor i = 0 to 20000\n    acc += math.sqrt(i)\nplot(acc)\n')
    r = core.run_engine(s, timeout_s=1)
    assert not r['ok'] and r['error']['type'] in ('TIMEOUT', 'RUNTIME_ERROR')


def test_loop_limit_is_enforced(tmp_path):
    s = tmp_path / 'loop.pine'
    s.write_text('//@version=6\nindicator("loop")\nint n = 0\nwhile true\n    n += 1\nplot(n)\n')
    r = core.run_engine(s, timeout_s=60)
    assert not r['ok']                                   # never an endless run reported as success


def test_script_size_limit(tmp_path):
    s = tmp_path / 'big.pine'
    s.write_text('//@version=6\nindicator("big")\n' + '// x\n' * 200000 + 'plot(close)\n')
    rc, e = cli('validate', str(s))
    assert rc == 4 and e['errors'][0]['code'] == 'resource_limit'
