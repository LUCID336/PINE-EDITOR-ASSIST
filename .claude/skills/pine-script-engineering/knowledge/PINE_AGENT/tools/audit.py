"""Six reproducible local gates. These are not six independent exhaustive literature reviews or Pine compilation."""
import csv, json, re, subprocess, sys
from pathlib import Path
p=Path(__file__).resolve().parents[1]
def read(name): return (p/name).read_text(encoding='utf8')
def rows(name):
    with (p/name).open(encoding='utf8') as f: return list(csv.DictReader(f))
def gate(n,title,condition):
    print(f'{n}: {title}: {"PASS" if condition else "FAIL"}')
    if not condition: raise AssertionError(title)
manual=rows('references/manual-index.csv'); symbols=rows('references/symbol-catalog.csv')
gate(1,'TOC inventory and unique candidate IDs, explicit incomplete coverage',len(manual)==78 and len({r['id'] for r in manual})==78 and len({r['symbol'] for r in symbols})==len(symbols) and 'FULL_REFERENCE' in read('audit/OPEN_ITEMS.md'))
ps=list((p/'examples').glob('*.pine'))
gate(2,'Pine header and single declaration static checks',len(ps)==4 and all(s.read_text().startswith('//@version=6\n') and len(re.findall(r'^(?:indicator|strategy|library)\(',s.read_text(),re.M))==1 for s in ps) and all(f'v{i}' in read('RESEARCH.md') for i in range(1,7)))
h=read('examples/hybrid_indicator.pine')
gate(3,'HTF offset/guard, confirmation, null representation (static)', 'close[1], lookahead = barmerge.lookahead_on' in h and 'timeframe.in_seconds(htf) <= timeframe.in_seconds()' in h and 'barstate.isconfirmed and barstate.isrealtime' in h and 'na(x) ? "null"' in h)
s=read('examples/strategy_baseline.pine')
gate(4,'Explicit emulator assumptions and quant validation policy',all(t in s for t in ('commission_value','slippage','calc_on_every_tick = false','process_orders_on_close = false','pyramiding = 0')) and all(t in read('RESEARCH.md') for t in ('Walk-forward','PBO','Deflated Sharpe','NO TRADE')))
schema=json.loads(read('references/feature-schema.json'))
gate(5,'Schema/feature plot contract',all('"f_'+key+'"' in h for key in schema['properties']['features']['required']) and 'confirmed' in schema['required'] and 'display.data_window' in h)
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=p,check=True)
gate(6,'Release prerequisites and residual blockers documented',all((p/f).is_file() for f in ('README.md','AGENTS.md','SKILL.md','RESEARCH.md','references/SOURCES.md','references/TEST_PLAN.md','audit/OPEN_ITEMS.md','audit/LOOPS.md')) and 'COMPILE/RUNTIME' in read('audit/OPEN_ITEMS.md'))
print(f'78 manual topics; {len(symbols)} candidate identifiers; 4 baseline Pine examples; Python regression suite passed. Pine compile NOT RUN; completeness NOT ESTABLISHED.')
