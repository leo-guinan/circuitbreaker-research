from fractions import Fraction
import unittest
import switching

class SwitchingTests(unittest.TestCase):
    def test_closed_odd_path_switches_and_scores(self):
        # a(+)-b(-), each has two same-sign neighbors. Both a guards are U.
        edges=[('a','b'),('a','c'),('a','d'),('b','e'),('b','f'),('c','g'),('c','h'),('d','i'),('d','j')]
        signs={v:1 for edge in edges for v in edge}; signs.update(b=-1,e=-1,f=-1)
        r=switching.apply(edges,signs,lam=Fraction(35,71))
        self.assertEqual(r['cover'],{'b'})
        self.assertEqual(r['switches'],1)
        self.assertEqual(r['labels'][0],1)
        self.assertEqual(r['costs']['b'],Fraction(1))
        self.assertTrue(r['valid_cover'])

    def test_boundary_crossing_is_unresolved_and_never_switched(self):
        edges=[('a','b')]; signs={'a':1,'b':-1}
        r=switching.apply(edges,signs)
        self.assertEqual(r['switches'],0)
        self.assertEqual(r['unresolved_paths'],1)
        self.assertTrue(r['valid_cover'])

    def test_partial_switch_boundary_label_and_guard_unknown(self):
        edges=[('p','n'),('n','q'),('q','z'),('p','c'),('p','d'),('n','nn'),('q','t'),('z','zz'),('z','zzz'),('c','c1'),('c','c2'),('d','d1'),('d','d2')]
        signs={v:1 for e in edges for v in e}
        for v in ('n','z','nn','zz','zzz'): signs[v]=-1
        r=switching.apply(edges,signs)
        self.assertEqual(r['switches'],1)
        self.assertEqual(r['boundary_edges'],{frozenset(('n','q'))})
        self.assertEqual(r['labels'][1],-1)
        self.assertEqual(r['unknown_guards'],1)
        self.assertFalse(r['canonical_complete'])
        self.assertEqual(len(r['cover']),len(r['base_cover']))

    def test_guard_w1_w2_and_vodd(self):
        # Crossing arm x-y terminates after one additional edge at y.
        edges=[('p','w'),('w','x'),('w','s'),('x','y'),('x','x1'),('y','y1'),('y','y2')]
        signs={v:1 for e in edges for v in e}; signs.update(x=-1,x1=-1)
        self.assertEqual(switching.guard(edges,signs,'p','w'),'W1')
        edges2=edges+[('s','t'),('s','s1'),('t','t1'),('t','t2')]
        signs2={v:1 for e in edges2 for v in e}; signs2.update(x=-1,x1=-1,s=-1,s1=-1)
        self.assertEqual(switching.guard(edges2,signs2,'p','w'),'W2')
        edges3=[('p','w'),('w','x'),('w','s'),('x','x1'),('x','x2'),('s','s1'),('s','s2')]
        signs3={v:1 for e in edges3 for v in e}; signs3.update(x=-1,x1=-1,x2=-1)
        self.assertEqual(switching.guard(edges3,signs3,'p','w'),'Vodd')

    def test_negative_root_guard_symmetric(self):
        edges=[('p','w'),('w','x'),('w','y')]
        signs={'p':-1,'w':-1,'x':-1,'y':-1}
        self.assertEqual(switching.guard(edges,signs,'p','w'),'U')

if __name__=='__main__': unittest.main()
