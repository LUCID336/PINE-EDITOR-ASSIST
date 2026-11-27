"""Copy a complete Pine script to a clean TXT deliverable. Not a compiler."""
import argparse
import re
from pathlib import Path

def export(source, dest, legacy_v1=False):
    source, dest = Path(source), Path(dest)
    if dest.suffix.lower() != '.txt':
        raise ValueError('Destination must be .txt')
    code = source.read_text(encoding='utf-8-sig')
    if not code.strip() or re.search(r'^\s*(?:```|~~~)', code, re.M):
        raise ValueError('Empty code or Markdown fences')
    versions = re.findall(r'^\s*//@version\s*=\s*(\d+)\s*$', code, re.M)
    if len(versions) != 1 and not (legacy_v1 and not versions):
        raise ValueError('Expected exactly one Pine version annotation (or explicit legacy v1)')
    if versions and versions[0] not in ('1','2','3','4','5','6'):
        raise ValueError('Version outside known v1-v6; verify official docs and update exporter')
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = (code.rstrip('\n') + '\n').encode('utf-8')
    with dest.open('xb') as f:
        f.write(payload)
    if dest.read_bytes() != payload:
        raise IOError('Output verification failed')
    return dest.resolve()

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source'); p.add_argument('dest'); p.add_argument('--legacy-v1',action='store_true')
    a=p.parse_args(); print(export(a.source,a.dest,a.legacy_v1))
