"""Reference local business validator, not a production receiver."""
import math
FEATURES={'ema','rsi','atr','rvol','htf_close'}
FIELDS={'schema_version','build','config_id','symbol','timeframe','bar_open_ms','bar_close_ms','confirmed','quality','features'}
def validate(event):
    if not isinstance(event,dict) or set(event)!=FIELDS: raise ValueError('event fields')
    if event['schema_version']!='1.0' or event['confirmed'] is not True: raise ValueError('version/confirmation')
    if any(not isinstance(event[x],str) or not event[x].strip() for x in ('build','config_id','symbol','timeframe')): raise ValueError('identifier')
    a,b=event['bar_open_ms'],event['bar_close_ms']
    if type(a) is not int or type(b) is not int or not 0<=a<b: raise ValueError('bar timestamps')
    fs=event['features']
    if not isinstance(fs,dict) or set(fs)!=FEATURES: raise ValueError('feature fields')
    for key,v in fs.items():
        if v is not None and (type(v) not in (int,float) or not math.isfinite(v)): raise ValueError('numeric values')
        if v is not None and key=='rsi' and not 0<=v<=100: raise ValueError('rsi range')
        if v is not None and key in ('atr','rvol') and v<0: raise ValueError('nonnegative feature')
    expected='MISSING' if any(v is None for v in fs.values()) else 'READY'
    if event['quality']!=expected: raise ValueError('quality mismatch')
    return event

def dedup_key(event):
    validate(event)
    return tuple(event[k] for k in ('build','config_id','symbol','timeframe','bar_open_ms'))
