import unittest
from fractions import Fraction
from itertools import product
import numpy as np
import wave_dp as w

class Tests(unittest.TestCase):
    def test_tree(self):
        edges, internal = w.tree(2)
        self.assertEqual((len(edges), len(internal)), (9, 4))
    def test_wave(self):
        x = w.sample_wave(2, 100000, 1234)
        edges, internal = w.tree(2)
        self.assertEqual(x.shape, (100000, 10))
        for v in internal:
            neighbors = [b if a == v else a for a,b in edges if v in (a,b)]
            np.testing.assert_allclose(x[:,neighbors].sum(axis=1), 2*np.sqrt(2)*x[:,v], atol=1e-12)
        cov = np.cov(x, rowvar=False)
        self.assertLess(abs(cov[0,0]-1), .02)
        self.assertLess(abs(cov[0,1]-2*np.sqrt(2)/3), .02)
        self.assertLess(abs(cov[1,2]-5/6), .02)
        np.testing.assert_array_equal(x[:3], w.sample_wave(2, 100000, 1234)[:3])
    def test_dp_exhaustive(self):
        edges, vertices = w.tree(2)
        for a in product((0,1), repeat=len(vertices)):
            anchors = dict(zip(vertices,a))
            for lam in (Fraction(35,71), Fraction(0), Fraction(3,2)):
                got, bits = w.solve(edges, anchors, lam)
                oracle = min(w.evaluate(edges,anchors,b,lam) for b in product((0,1), repeat=len(edges)))
                self.assertEqual(got, oracle)
                self.assertEqual(got, w.evaluate(edges,anchors,bits,lam))
    def test_comparison(self):
        e, v = w.tree(1); a={0:0}; lam=Fraction(35,71)
        c=w.compare(e,a,(1,1,1),(0,0,0),lam)
        self.assertEqual(c['root_gap'],lam)
        self.assertEqual(c['global_gap'],lam)
        self.assertEqual(c['disagreement_components'],[3])

if __name__ == '__main__': unittest.main()
