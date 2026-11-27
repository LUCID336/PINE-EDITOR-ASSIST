import json,csv,subprocess,sys
from pathlib import Path
from pine_lookup import lookup,ROUTES
p=Path(__file__).resolve().parents[1]
def load(n):return json.loads((p/'instructions'/n).read_text())
def gate(n,condition):
 assert condition,n
 print('PASS:',n)
t=load('topic-index.json');a=load('api-index.json');m=load('manifest.json')
with (p/'references/manual-index.csv').open() as f: old=list(csv.DictReader(f))
with (p/'references/symbol-catalog.csv').open() as f: sy=list(csv.DictReader(f))
gate('78/78 topic identities + sheets',len(t)==78 and {x['id'] for x in t}=={x['id'] for x in old} and all((p/x['path']).is_file() and all(x[k] for k in ('action','rationale','acceptance','source')) for x in t))
gate('612/612 candidates preserved + status',len(a)==612 and {x['symbol'] for x in a}=={x['symbol'] for x in sy} and all(x['status']=='CANDIDATE_UNVERIFIED' and (p/x['sheet']).is_file() for x in a))
gate('43 namespace files + valid references',len({x['sheet'] for x in a})==43 and all(set(x['topics'])<={r['id'] for r in t} for x in a))
gate('lookup exact/unknown/namespace + route paths',lookup('topic','M04')[0]['id']=='M04' and lookup('api','ta.ema')[0]['symbol']=='ta.ema' and not lookup('api','invalid_fake_xyz') and len(lookup('api','ta'))>1 and all(lookup('route',k)['topics'] and all((p/f).is_file() for f in lookup('route',k)['workflows']) for k in ROUTES))
gate('error-specific repair evidence',all(term in next(x['action'] for x in t if x['id']==i) for i,term in [('M52','compiled'),('M54','inline'),('M55','memory'),('M56','offset')]))
gate('source statuses and manifest',sum(x['source_status']=='SOURCE_ACCESSED_PARTIAL' for x in t)==31 and m['runtime_status']=='NOT_RUN' and m['candidate_count']==len(a) and all((p/f).is_file() for f in [m['entrypoint'],m['api_index'],m['topic_index']]) and all(json.loads(f.read_text()) for f in (p/'instructions/templates').glob('*.json')))
print('All v2 local gates passed. Pine compiler NOT_RUN. Complete API coverage NOT ESTABLISHED.')
