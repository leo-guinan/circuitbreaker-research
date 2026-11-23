import unittest
import experiment
class Integration(unittest.TestCase):
 def test_group_conservation_and_exact_gap(self):
  self.assertTrue(callable(getattr(experiment,'wave_experiment',None)))
  d=experiment.wave_experiment(3,20,42)
  self.assertEqual(d['count'],20)
  self.assertGreaterEqual(d['gap_numerator_total'],0)
  self.assertEqual(sum(g['count'] for g in d['groups']),20)
  self.assertEqual(sum(g['gap_numerator'] for g in d['groups']),d['gap_numerator_total'])
  self.assertEqual(d['lambda'],'35/71')
if __name__=='__main__': unittest.main()
