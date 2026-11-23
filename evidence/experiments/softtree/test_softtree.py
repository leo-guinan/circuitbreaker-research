import unittest
from itertools import product
from softtree import solve, brute, local

class Behavior(unittest.TestCase):
    def test_star_unanimous_witness(self):
        e=[(0,1),(0,2),(0,3)]
        self.assertEqual(solve(e,{0:1}), (0,(1,1,1)))
        self.assertEqual(brute(e,{0:1}), (0,(1,1,1)))
    def test_all_anchors_and_witnesses(self):
        e=[(0,1),(0,2),(0,3),(1,4),(1,5),(2,6),(2,7)]
        for a in product((0,1),repeat=3):
            anchors=dict(zip((0,1,2),a))
            d=solve(e,anchors); b=brute(e,anchors); l=local(e,anchors)
            self.assertEqual(d[0],b[0]); self.assertGreaterEqual(l[0],d[0])
            for cost,bits in (d,b,l):
                self.assertEqual(len(bits),len(e))
                total=0
                for v,anchor in anchors.items():
                    incident=[bits[i] for i,(x,y) in enumerate(e) if v in (x,y)]
                    total += 2 if len(set(incident))>1 else int(incident[0]!=anchor)
                self.assertEqual(cost,total)
    def test_no_vertices(self):
        self.assertEqual(solve([(0,1)],{}),(0,(0,)))

if __name__=='__main__': unittest.main()
