import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import validate


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'snapshots' / 'one').mkdir(parents=True)
        (self.root / 'snapshots' / 'one' / 'proof.txt').write_text('candidate\n')
        manifest = {'proof.txt': hashlib.sha256(b'candidate\n').hexdigest()}
        self.entry = {'id': 'one', 'claim': 'claim', 'authors': ['alice'], 'dependencies': [],
                      'research_status': 'candidate', 'review_status': 'pending',
                      'external_status': 'not_submitted', 'evidence': ['evidence/receipt'],
                      'snapshot': {'files': manifest, 'digest': validate.digest(manifest)}, 'reviews': []}
        self.agents = [{'id': 'alice', 'name': 'Alice'}, {'id': 'bob', 'name': 'Bob'}]
        self.entries = [self.entry]
    def tearDown(self): self.tmp.cleanup()
    def check(self):
        (self.root / 'REGISTRY.json').write_text(json.dumps({'version': 1, 'agents': self.agents}))
        (self.root / 'SCOREBOARD.json').write_text(json.dumps({'version': 1, 'entries': self.entries}))
        return validate.validate(self.root)
    def test_valid(self): self.assertEqual(self.check(), [])
    def test_self_review_rejected(self):
        self.entry['reviews'] = [{'reviewer': 'alice', 'verdict': 'approved', 'snapshot_digest': self.entry['snapshot']['digest'], 'evidence': 'receipt'}]
        self.entry['review_status'] = 'approved'
        self.assertTrue(any('self or unknown' in x for x in self.check()))
    def test_independent_review(self):
        self.entry['reviews'] = [{'reviewer': 'bob', 'verdict': 'approved', 'snapshot_digest': self.entry['snapshot']['digest'], 'evidence': 'receipt'}]
        self.entry['review_status'] = 'approved'; self.entry['research_status'] = 'reviewed'
        self.assertEqual(self.check(), [])
    def test_status_distinct(self):
        self.entry['external_status'] = 'approved'
        self.assertTrue(any('external status' in x for x in self.check()))
        self.entry['external_status'] = 'accepted'; self.entry['research_status'] = 'reviewed'
        self.assertTrue(any('reviewed needs approval' in x for x in self.check()))
    def test_missing_dependency(self):
        self.entry['dependencies'] = ['missing']
        self.assertTrue(any('dependencies' in x for x in self.check()))
    def test_dependency_cycle(self):
        second = copy.deepcopy(self.entry); second['id'] = 'two'; second['dependencies'] = ['one']
        (self.root / 'snapshots' / 'two').mkdir(); (self.root / 'snapshots' / 'two' / 'proof.txt').write_text('candidate\n')
        self.entry['dependencies'] = ['two']; self.entries.append(second)
        self.assertTrue(any('cycle' in x for x in self.check()))
    def test_immutable_bytes(self):
        (self.root / 'snapshots' / 'one' / 'proof.txt').write_text('changed')
        self.assertTrue(any('hash mismatch' in x for x in self.check()))
    def test_extra_file_and_symlink(self):
        (self.root / 'snapshots' / 'one' / 'extra').symlink_to('proof.txt')
        self.assertTrue(any('symlink' in x for x in self.check()))
    def test_stale_review(self):
        self.entry['reviews'] = [{'reviewer': 'bob', 'verdict': 'approved', 'snapshot_digest': '0'*64, 'evidence': 'receipt'}]
        self.assertTrue(any('stale review' in x for x in self.check()))
    def test_traversal_rejected(self):
        self.entry['snapshot']['files']['../outside'] = '0'*64
        self.assertTrue(any('invalid snapshot manifest' in x for x in self.check()))

if __name__ == '__main__': unittest.main()
