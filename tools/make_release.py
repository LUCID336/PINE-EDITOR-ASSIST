"""Build the reproducible V5 master ZIP from git-tracked files.

Output: releases/dist/PINE_ENGINEERING_LAB_V5.zip and releases/dist/SHA256SUMS.txt (one line per file inside the ZIP,
plus the ZIP itself). node_modules is never packed: install.py restores the pinned runtime from package-lock.json.
Deterministic: sorted entries, fixed timestamps. Usage: python tools/make_release.py
"""
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
DIST = LAB / 'releases' / 'dist'
NAME = 'PINE_ENGINEERING_LAB_V5'
FIXED = (2026, 11, 27, 0, 0, 0)


def main():
    files = subprocess.run(['git', 'ls-files', '-z'], cwd=LAB, capture_output=True, check=True).stdout.decode().split('\0')
    files = sorted(f for f in files if f and not f.startswith('releases/dist/') and (LAB / f).is_file())
    DIST.mkdir(parents=True, exist_ok=True)
    zpath = DIST / f'{NAME}.zip'
    sums = []
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            data = (LAB / f).read_bytes()
            info = zipfile.ZipInfo(f'{NAME}/{f}', FIXED)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
            sums.append(f'{hashlib.sha256(data).hexdigest()}  {NAME}/{f}')
    zh = hashlib.sha256(zpath.read_bytes()).hexdigest()
    (DIST / 'SHA256SUMS.txt').write_text('\n'.join(sums + [f'{zh}  {zpath.name}']) + '\n')
    print(f'{zpath.relative_to(LAB)}: {len(files)} files, {zpath.stat().st_size} bytes, sha256 {zh}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
