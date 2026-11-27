"""Build knowledge/reference/v6-api-ledger.json from refresh_reference.mjs output; write example corpus.
Usage: python build_ledger.py RAW_DIR [--date YYYY-MM-DD]"""
import collections, json, re, sys
from pathlib import Path
raw = Path(sys.argv[1]); date = sys.argv[sys.argv.index('--date') + 1] if '--date' in sys.argv else 'UNKNOWN'
d = json.loads((raw / 'v6_ledger_raw.json').read_text())
def params(sig):
    m = re.match(r'^[^(]*\((.*)\)\s*→', sig)
    return [p.strip() for p in m.group(1).split(',') if p.strip()] if m else []
entries = []
for x in d:
    e = {k: x[k] for k in ('id', 'kind', 'name', 'syntax', 'args', 'returns', 'type', 'summary', 'learn_more')}
    e['name'] = x['name'].removesuffix('()'); e['overload_params'] = [params(s) for s in x['syntax']]
    entries.append(e)
meta = {'source': 'https://www.tradingview.com/pine-script-reference/v6/', 'retrieved': date,
        'method': 'Headless Chromium render of the public official reference; structured extraction.',
        'status': 'VERIFIED_FROM_OFFICIAL_REFERENCE_SNAPSHOT',
        'caveat': 'Snapshot only; re-extract after release-note changes. Argument qualifier labels are copied from the page; overload-specific qualifiers may differ per overload.',
        'counts': dict(collections.Counter(e['kind'] for e in entries))}
out = Path(__file__).resolve().parents[2] / 'knowledge' / 'reference' / 'v6-api-ledger.json'
out.write_text(json.dumps({'meta': meta, 'entries': entries}, indent=1, ensure_ascii=False))
corpus = raw / 'corpus'; corpus.mkdir(exist_ok=True)
n = 0
for i, ex in enumerate(json.loads((raw / 'examples.json').read_text())):
    if '//@version=6' in ex['code']:
        (corpus / f"{i:03d}_{re.sub(r'[^A-Za-z0-9_.]', '_', ex['id'])}.pine").write_text(ex['code']); n += 1
print(out, meta['counts'], 'v6 examples:', n, '->', corpus)
