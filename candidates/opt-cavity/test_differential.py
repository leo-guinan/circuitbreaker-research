"""Differential checks against the frozen certificate implementation."""
import importlib.util
import random
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent / 'baseline' / 'b346dab1'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

original = load('original_cavity', BASE / 'cavity.py')
candidate = load('candidate_cavity', HERE / 'cavity.py')

class Differential(unittest.TestCase):
    def test_lmlo_exact_arithmetic(self):
        rng = random.Random(118)
        pairs = [(0,0),(1,1),(0,7),(1,10**50),(10**50,1)]
        pairs += [(rng.randrange(10**12), rng.randrange(10**12)) for _ in range(10000)]
        for a,b in pairs:
            self.assertEqual(original.lmlo(a,b), candidate.lmlo(a,b))
    def test_small_cavity_grids(self):
        for args in [(8, 4, 2), (16, 6, 4), (24, 8, 6)]:
            with self.subTest(args=args):
                self.assertEqual(original.cavity(*args), candidate.cavity(*args))

    def test_geo_interp(self):
        rng = random.Random(73)
        for _ in range(10000):
            a,b = rng.randrange(10**10),rng.randrange(10**10)
            den = rng.randrange(1,1000); num = rng.randrange(-1,den+2)
            self.assertEqual(original.geo_interp(a,b,num,den), candidate.geo_interp(a,b,num,den))

if __name__ == '__main__': unittest.main()
