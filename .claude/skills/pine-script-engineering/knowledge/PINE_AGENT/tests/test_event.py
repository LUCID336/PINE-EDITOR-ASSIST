import unittest, copy, json
from tools.event_validation import validate, dedup_key
GOOD={'schema_version':'1.0','build':'example-1','config_id':'e20_r14_a14_v20_h1D','symbol':'EXAMPLE:TEST','timeframe':'60','bar_open_ms':1700000000000,'bar_close_ms':1700003600000,'confirmed':True,'quality':'READY','features':{'ema':100.5,'rsi':51.0,'atr':2.1,'rvol':1.2,'htf_close':99.0}}
class TestEvent(unittest.TestCase):
    def test_roundtrip(self): self.assertEqual(validate(json.loads(json.dumps(GOOD))),GOOD)
    def test_missing(self):
        e=copy.deepcopy(GOOD); e['features']['rvol']=None; e['quality']='MISSING'; validate(e)
    def test_quality_mismatch(self):
        e=copy.deepcopy(GOOD); e['features']['rvol']=None
        with self.assertRaises(ValueError): validate(e)
    def test_invalid_number(self):
        for v in (float('nan'),float('inf'),True,'12',-1):
            e=copy.deepcopy(GOOD); e['features']['atr']=v
            with self.assertRaises(ValueError): validate(e)
    def test_confirmation(self):
        e=copy.deepcopy(GOOD); e['confirmed']=False
        with self.assertRaises(ValueError): validate(e)
    def test_timestamps(self):
        e=copy.deepcopy(GOOD); e['bar_close_ms']=e['bar_open_ms']
        with self.assertRaises(ValueError): validate(e)
    def test_dedup(self):
        e=copy.deepcopy(GOOD); self.assertEqual(dedup_key(e),dedup_key(GOOD)); e['config_id']='other'; self.assertNotEqual(dedup_key(e),dedup_key(GOOD))
    def test_extra_field(self):
        e=copy.deepcopy(GOOD); e['secret']='not allowed'
        with self.assertRaises(ValueError): validate(e)
    def test_rsi(self):
        e=copy.deepcopy(GOOD); e['features']['rsi']=101
        with self.assertRaises(ValueError): validate(e)
if __name__=='__main__': unittest.main()
