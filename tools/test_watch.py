import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = str(Path(__file__).with_name('watch.py'))

class Integration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.base = Path(self.tmp.name); self.remote = self.base/'remote.git'; self.work = self.base/'work'; self.state = self.base/'state'
        self.g('init', '--bare', '-q', str(self.remote)); self.g('init', '-q', str(self.work))
        self.g('-C', str(self.work), 'config', 'user.name', 'Test'); self.g('-C', str(self.work), 'config', 'user.email', 'test@example.invalid')
        self.g('-C', str(self.work), 'checkout', '-qb', 'research/antigravity')
    def tearDown(self): self.tmp.cleanup()
    def g(self, *args):
        return subprocess.run(['/usr/bin/git', *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
    def commit(self, text):
        (self.work/'result.txt').write_text(text)
        self.g('-C', str(self.work), 'add', 'result.txt'); self.g('-C', str(self.work), 'commit', '-qm', text)
        return self.g('-C', str(self.work), 'rev-parse', 'HEAD')
    def push(self): self.g('-C', str(self.work), 'push', '-q', '--force', str(self.remote), 'HEAD:refs/heads/research/antigravity')
    def runwatch(self, remote=None):
        return subprocess.run([sys.executable, SCRIPT, '--remote', str(remote or self.remote), '--branch', 'research/antigravity', '--state-dir', str(self.state)], capture_output=True, text=True)
    def state_data(self): return json.loads((self.state/'state.json').read_text())
    def test_end_to_end(self):
        self.assertEqual(self.runwatch().stdout, '') # branch absent
        a = self.commit('baseline'); self.push()
        self.assertEqual(self.runwatch().stdout, '')
        self.assertEqual(self.state_data()['tip'], a)
        self.assertEqual(self.runwatch().stdout, '')
        b = self.commit('first outcome'); c = self.commit('second outcome'); self.push()
        event = json.loads(self.runwatch().stdout)
        self.assertEqual(event['commits'], [b, c]); self.assertEqual(event['previous_tip'], a)
        self.assertEqual(self.runwatch().stdout, '')
        # A failed fetch/remote lookup never advances the cursor.
        self.remote.rename(self.base/'offline.git'); self.assertNotEqual(self.runwatch().returncode, 0)
        self.assertEqual(self.state_data()['tip'], c); (self.base/'offline.git').rename(self.remote)
        self.g('-C', str(self.work), 'push', '-q', str(self.remote), ':refs/heads/research/antigravity')
        self.assertEqual(json.loads(self.runwatch().stdout)['kind'], 'branch_missing')
        self.assertEqual(self.runwatch().stdout, '')
        self.push(); self.assertEqual(json.loads(self.runwatch().stdout)['kind'], 'branch_restored')
        # Forced rewind has an empty new-commit set but still reports the changed exact tip.
        self.g('-C', str(self.work), 'reset', '--hard', a); self.push()
        ev = json.loads(self.runwatch().stdout); self.assertEqual((ev['previous_tip'], ev['tip'], ev['commits']), (c, a, []))
        events = self.state_data()['events']; self.assertEqual(len(events), 4)
        self.assertEqual([e['sequence'] for e in events], [1, 2, 3, 4])
        self.assertEqual(events[0]['commits'], [b, c])
    def test_lock_and_credentials(self):
        self.commit('base'); self.push(); self.runwatch()
        before = (self.state/'state.json').read_bytes()
        with open(self.state/'lock', 'a+b') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            r = self.runwatch(); self.assertEqual((r.returncode, r.stdout), (0, ''))
        self.assertEqual(before, (self.state/'state.json').read_bytes())
        r = self.runwatch('https://user:secret@example.invalid/repo')
        self.assertNotEqual(r.returncode, 0); self.assertNotIn('secret', r.stderr + r.stdout)
        self.assertEqual(before, (self.state/'state.json').read_bytes())

if __name__ == '__main__': unittest.main(verbosity=2)
