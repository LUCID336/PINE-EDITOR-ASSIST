"""Offline exact/substring lookup of original guidance, not an API signature resolver."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/'instructions'/name).read_text(encoding='utf-8'))
ROUTES={
'indicator':('M02 M04 M05 M13 M29 M35 M39 M61','ENGINEERING HUMAN_AI TEMPORAL'),
'strategy':('M04 M38 M39 M41 M49 M64','ENGINEERING TEMPORAL QUANT'),
'library':('M05 M14 M17 M36','ENGINEERING'),
'migration':('M70 M71 M72 M73 M74 M75 M76','ENGINEERING MIGRATION'),
'debug':('M46 M47 M49 M50 M51 M52 M53 M54 M55 M56','ENGINEERING DEBUG'),
'ai':('M29 M30 M32 M35 M38 M39 M42 M58','ENGINEERING HUMAN_AI TEMPORAL'),
'human':('M21 M25 M28 M29 M30 M31 M35 M54 M69','ENGINEERING HUMAN_AI'),
'mtf':('M04 M33 M38 M39 M43 M44','ENGINEERING TEMPORAL'),
'optimization':('M12 M47 M49 M52 M55','ENGINEERING DEBUG'),
'quant':('M34 M38 M39 M41 M61 M64','ENGINEERING QUANT TEMPORAL')}
def lookup(kind,q):
 q=q.strip().casefold()
 if not q: return []
 if kind=='route':
  if q not in ROUTES:return []
  ids,work=ROUTES[q];return {'topics':[r for r in load('topic-index.json') if r['id'] in ids.split()],'workflows':[f'instructions/workflows/{x}.md' for x in work.split()]}
 if kind=='topic':
  data=load('topic-index.json'); exact=[r for r in data if q in (r['id'].casefold(),r['title'].casefold())];return exact or [r for r in data if q in (' '.join([r['title'],r['section'],r['action'],r['path']])).casefold()]
 data=load('api-index.json');exact=[r for r in data if r['symbol'].casefold()==q];return exact or [r for r in data if q in r['symbol'].casefold() or q==r['namespace'].casefold()]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('kind',choices=['topic','api','route']);p.add_argument('query');p.add_argument('--json',action='store_true');args=p.parse_args();out=lookup(args.kind,args.query)
 if args.json:print(json.dumps(out,ensure_ascii=False,indent=2))
 elif isinstance(out,dict):
  for r in out['topics']:print(r['id'],r['title'],r['path'],r['source_status'])
  for f in out['workflows']:print(f)
 else:
  for r in out:print(r.get('id',r.get('symbol')),r.get('path',r.get('sheet')),r.get('source_status',r.get('status')))
 if not out:
  import sys; print('No local match; consult official reference. Absence is not evidence.',file=sys.stderr);return 1
 return 0
if __name__=='__main__':raise SystemExit(main())
