import unittest
from legacy_experiment import run

class ExperimentTest(unittest.TestCase):
    def test_run_emits_verified_witnesses_and_matched_samples(self):
        data=run()
        self.assertGreater(len(data['cases']),0)
        self.assertTrue(all(c['dp']['cost2']==c['brute']['cost2'] for c in data['cases'] if c['brute'] is not None))
        self.assertTrue(all(c['local']['cost2']>=c['dp']['cost2'] for c in data['cases']))
        self.assertTrue(any(c['local']['cost2']>c['dp']['cost2'] for c in data['cases']))

if __name__=='__main__': unittest.main()
