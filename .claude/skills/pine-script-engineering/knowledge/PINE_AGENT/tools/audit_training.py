"""Six reproducible local V3 checks. No Pine compilation or course-completion claim."""
import json, re, sys, subprocess
from pathlib import Path
from pine_training import load, next_labs, lookup_tips
from pine_lookup import ROUTES
p=Path(__file__).resolve().parents[1]
def gate(name, passed):
    if not passed: raise AssertionError(name)
    print('PASS:',name)
sources=load('sources.json'); labs=load('curriculum.json'); tips=load('tips.json')
ids={s['id'] for s in sources}
gate('01 sources: unique IDs, retrieval and access status',len(ids)==len(sources)==37 and all(s['url'].startswith('https://') and s['retrieval'] and s['access'] and s['checked'] for s in sources))
seen=set()
for lab in labs:
    assert set(lab['prerequisites'])<=seen and set(lab['sources'])<=ids and lab['route'] in ROUTES
    assert (p/lab['path']).is_file() and (p/lab['solution']).is_file() and lab['checks']
    seen.add(lab['id'])
gate('02 curriculum: 16 unique labs, DAG, references and acceptance criteria',len(seen)==len(labs)==16)
ps=list((p/'training/solutions').glob('*.pine'))
gate('03 Pine static sanity: 14 v6 headers, single declaration, uncompiled state',len(ps)==14 and all(f.read_text().startswith('//@version=6\n') and len(re.findall(r'^(?:indicator|strategy|library)\(',f.read_text(),re.M))==1 for f in ps) and all(l['runtime_status']=='NOT_RUN' for l in labs if l['solution'].endswith('.pine')))
gate('04 tips/quiz: 40 IDs and source pointers, 18 question/answer pairs',len({x['id'] for x in tips})==len(tips)==40 and all(set(re.findall(r'\bS\d{2}\b',x['sources']))<=ids and x['test'] for x in tips) and all(len(re.findall(r'^\d+\. ',(p/'training'/f).read_text(),re.M))==18 for f in ['QUIZ.md','QUIZ_KEY.md']))
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=p,check=True)
gate('05 local routing and fixture/regression tests', [x['id'] for x in next_labs()]==['L01'] and len(lookup_tips('repaint'))>=3)
manifest=json.loads((p/'instructions/manifest.json').read_text())
gate('06 integration and honest progress defaults',manifest['version']=='3.0' and manifest['training_labs']==len(labs) and all('training/START_HERE.md' in (p/f).read_text() for f in ['AGENTS.md','SKILL.md','README.md','instructions/START_HERE.md']) and all(x['status']=='NOT_RUN' for x in load('templates/progress.json')['lessons'].values()) and 'TRAINING:' in (p/'audit/OPEN_ITEMS.md').read_text())
print('V3 local checks complete; Pine runtime NOT_RUN; external courses not completed.')
