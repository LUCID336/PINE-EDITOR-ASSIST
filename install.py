"""Pine Engineering Lab V5 installer (Windows, macOS, Linux). Python >= 3.10 and Node.js >= 20 required.

Steps: 1) check Python/Node/npm  2) install the pinned local runtime (PineTS 0.13.1) with `npm ci --ignore-scripts`
3) write .mcp.json for the optional local MCP wrapper with this Python interpreter (existing file backed up)
4) optional --claude-user: copy the lab skills and agents to ~/.claude (conflicts backed up, never silently replaced)
5) offline self-test (network blocked).  No settings/permission changes, no login, no paid service.
Usage: python install.py [--dry-run] [--skip-npm] [--claude-user] [--no-selftest]
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LAB = Path(__file__).resolve().parent
RUNTIME = LAB / 'tools' / 'runtime'


def say(msg):
    print(f'[install] {msg}')


def version_tuple(s):
    return tuple(int(x) for x in s.strip().lstrip('v').split('.')[:2])


def check(dry):
    ok = True
    if sys.version_info < (3, 10):
        say(f'Python {sys.version.split()[0]} found; 3.10+ required'); ok = False
    node, npm = shutil.which('node'), shutil.which('npm')
    if not node or not npm:
        say('Node.js/npm not found. Install Node.js LTS (>= 20) from https://nodejs.org and reopen the terminal.'); return False
    nv = subprocess.run([node, '--version'], capture_output=True, text=True).stdout
    if version_tuple(nv) < (20, 0):
        say(f'Node {nv.strip()} found; >= 20 required'); ok = False
    for mod in ('pytest', 'jsonschema'):
        try:
            __import__(mod)
        except ImportError:
            say(f'Python package "{mod}" missing (needed for the test suites): {sys.executable} -m pip install {mod}')
    say(f'Python {sys.version.split()[0]}, Node {nv.strip()}, npm at {npm}')
    return ok


def backup(path):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    b = path.with_name(path.name + f'.backup-{stamp}')
    shutil.move(str(path), str(b))
    return b


def install_runtime(dry):
    if dry:
        say(f'would run: npm ci --ignore-scripts  (in {RUNTIME})'); return True
    npm = shutil.which('npm')
    p = subprocess.run([npm, 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], cwd=RUNTIME, text=True, capture_output=True)
    if p.returncode != 0:
        say('npm ci failed:\n' + (p.stderr or p.stdout)[-1500:]); return False
    pkg = json.loads((RUNTIME / 'node_modules' / 'pinets' / 'package.json').read_text())
    say(f"runtime installed: pinets {pkg['version']} (license {pkg.get('license')})")
    return pkg['version'] == '0.13.1'


def write_mcp(dry):
    cfg = {'mcpServers': {'pinelab': {'type': 'stdio', 'command': sys.executable, 'args': ['tools/pinelab_mcp.py'], 'env': {}}}}
    target = LAB / '.mcp.json'
    if dry:
        say(f'would write {target} (command = {sys.executable})'); return
    if target.exists() and json.loads(target.read_text()) != cfg:
        say(f'backed up existing .mcp.json -> {backup(target).name}')
    target.write_text(json.dumps(cfg, indent=2) + '\n')
    say('.mcp.json written (local stdio server, no secrets, no remote endpoint)')


def install_claude_user(dry):
    home = Path.home() / '.claude'
    pairs = [(p, home / 'skills' / p.name) for p in (LAB / '.claude' / 'skills').iterdir() if p.is_dir()]
    pairs += [(p, home / 'agents' / p.name) for p in (LAB / '.claude' / 'agents').glob('*.md')]
    for src, dst in pairs:
        if dry:
            say(f'would install {dst}' + (' (existing -> backup)' if dst.exists() else '')); continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            say(f'backup {dst} -> {backup(dst).name}')
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, dst)
    if not dry:
        say(f'installed {len(pairs)} skills/agents into {home}. Note: the lab tools are referenced relative to the lab folder.')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--skip-npm', action='store_true', help='use an existing tools/runtime/node_modules')
    ap.add_argument('--claude-user', action='store_true', help='also copy skills/agents into ~/.claude')
    ap.add_argument('--no-selftest', action='store_true')
    a = ap.parse_args()
    if not check(a.dry_run):
        return 1
    if not a.skip_npm and not install_runtime(a.dry_run):
        return 1
    write_mcp(a.dry_run)
    if a.claude_user:
        install_claude_user(a.dry_run)
    if a.dry_run or a.no_selftest:
        say('done (self-test not run)'); return 0
    say('running offline self-test ...')
    rc = subprocess.run([sys.executable, str(LAB / 'tools' / 'selftest.py')], cwd=LAB).returncode
    say('installation complete' if rc == 0 else 'self-test FAILED - see output above')
    return rc


if __name__ == '__main__':
    sys.exit(main())
