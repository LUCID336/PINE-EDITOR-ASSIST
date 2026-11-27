import json
import math
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from pine_training import next_labs, lookup_tips, load

class TrainingTests(unittest.TestCase):
    def setUp(self):
        self.f = load('fixtures/synthetic.json')
    def test_sma(self):
        c, n = self.f['close'], self.f['length']
        result = [None if i+1 < n else sum(c[i+1-n:i+1])/n for i in range(len(c))]
        self.assertEqual(result, self.f['expected_sma'])
    def test_changes(self):
        c = self.f['close']
        self.assertEqual([None] + [b-a for a,b in zip(c,c[1:])],self.f['expected_changes'])
    def test_bounded_buffer(self):
        b=[]
        for v in self.f['close']:
            b.append(v)
            if len(b)>self.f['length']: b.pop(0)
            self.assertLessEqual(len(b), self.f['length'])
        self.assertEqual(b,self.f['expected_buffer'])
    def test_sizing(self):
        s=self.f['sizing']
        self.assertEqual(math.floor(s['risk']/(s['distance']*s['point_value'])/s['step'])*s['step'],s['expected'])
    def test_friction(self):
        f=self.f['friction']
        self.assertEqual(f['gross']-sum(f['fees'])-sum(f['slippage']),f['expected'])
    def test_pivot_observation(self):
        f=self.f['pivot']; self.assertEqual(f['anchor']+f['right'],f['expected_observable'])
    def test_event_dedup_fixture(self):
        events=self.f['events']; unique={x['key']:x for x in events}
        self.assertEqual(len(unique),2)
        self.assertIsNone(json.loads(json.dumps(events[0]))['rsi'])
    def test_prerequisite_gate(self):
        self.assertEqual([x['id'] for x in next_labs()],['L01'])
        self.assertEqual([x['id'] for x in next_labs({'lessons':{'L01':{'status':'PASS','evidence':'lab-01-log.json'}}})],['L02'])
        self.assertEqual([x['id'] for x in next_labs({'lessons':{'L01':{'status':'PASS'}}})],['L01'])
    def test_tips_search(self):
        self.assertTrue(any(x['id']=='T11' for x in lookup_tips('HTF')))
        self.assertTrue(any(x['id']=='T11' for x in lookup_tips('repaint')))
        self.assertEqual(lookup_tips('not-a-real-needle-123'),[])
    def test_sources_and_routes(self):
        from pine_lookup import ROUTES
        ids={x['id'] for x in load('sources.json')}
        labs=load('curriculum.json'); seen=set()
        for l in labs:
            self.assertTrue(set(l['prerequisites']) <= seen)
            self.assertTrue(set(l['sources']) <= ids)
            self.assertIn(l['route'],ROUTES)
            self.assertTrue((ROOT/l['path']).is_file() and (ROOT/l['solution']).is_file())
            seen.add(l['id'])
        self.assertEqual(len(seen),16)
        self.assertEqual(len(load('tips.json')),40)
