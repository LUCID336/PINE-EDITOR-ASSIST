import sys,glob,re,random
sys.path.insert(0,__import__('os').path.join(__import__('os').path.dirname(__file__),'..')); import pine_static_check as p
L=p.load_ledger(); random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 7)
files=sorted(glob.glob(sys.argv[1] + '/*.pine'))
pats={'fun':(r'(?<![\w.])((?:ta|math|request|str|array|strategy|input|color|label|line|box|table)\.[a-z_]+)\s*\(','x'),
 'arg':(r'[(,]\s*([a-z_]+)\s*=(?!=)','zz'),
 'var':(r'(?<![\w.])((?:barstate|syminfo|timeframe|color|shape|location|strategy|session)\.[a-z_]+)(?![\w.(])','q')}
stats={k:[0,0] for k in pats}; missed=[]
for f in files:
    s=open(f).read(); code=p.strip_code(s)
    for k,(rx,suf) in pats.items():
        ms=list(re.finditer(rx,code))
        if not ms: continue
        m=random.choice(ms); mut=s[:m.end(1)]+suf+s[m.end(1):]
        ok=any(x['severity']=='ERROR' for x in p.check(mut,L)); stats[k][0]+=1; stats[k][1]+=ok
        if not ok: missed.append((k,f,m.group(1)))
for k,(n,d) in stats.items(): print(f'{k}: detected {d}/{n} = {d/n:.1%}')
print(missed[:12])
