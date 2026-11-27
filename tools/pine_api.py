"""Look up official Pine v6 signatures from the verified reference snapshot.
Usage: python pine_api.py NAME            exact entry (e.g. request.security, barstate.isconfirmed)
       python pine_api.py --search TEXT   substring search over names
       python pine_api.py NAME --json"""
import json, sys
from pathlib import Path
L = json.loads((Path(__file__).resolve().parent.parent / 'knowledge' / 'reference' / 'v6-api-ledger.json').read_text(encoding='utf-8'))
args = [a for a in sys.argv[1:] if a != '--json']
if not args:
    print(__doc__); sys.exit(2)
if args[0] == '--search':
    for e in L['entries']:
        if args[1].lower() in e['name'].lower():
            print(f"{e['kind']:5} {e['name']}")
    sys.exit(0)
hits = [e for e in L['entries'] if e['name'] == args[0] or e['name'].split('<')[0] == args[0]]
if not hits:
    print(f'NOT IN v6 SNAPSHOT ({L["meta"]["retrieved"]}): {args[0]} -- do not use without official evidence'); sys.exit(1)
for e in hits:
    if '--json' in sys.argv:
        print(json.dumps(e, indent=1, ensure_ascii=False)); continue
    print(f"[{e['kind']}] {e['name']}  — {e['summary']}")
    for s in e['syntax']: print('  ', s)
    for a in e['args']: print('   arg:', a)
    if e['type']: print('   type:', e['type'])
    if e['returns']: print('   returns:', e['returns'][:160])
    print('   source:', L['meta']['source'] + '#' + e['id'], '| retrieved', L['meta']['retrieved'])
