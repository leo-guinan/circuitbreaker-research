"""Run alternating fresh interpreters against identical frozen input, compare stdout."""
import hashlib, os, statistics, subprocess, sys, time
from pathlib import Path
here = Path(__file__).resolve().parent
base = here.parent.parent / 'baseline' / 'b346dab1'
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
outputs = []
times = {'baseline': [], 'candidate': []}
for run in range(3):
    for name, path in ([('baseline',base),('candidate',here)] if run % 2 == 0 else [('candidate',here),('baseline',base)]):
        start = time.perf_counter()
        p = subprocess.run([sys.executable, str(path/'certify.py')], cwd=path, env=env, capture_output=True, timeout=120)
        elapsed = time.perf_counter()-start
        assert p.returncode == 0, (name,p.returncode,p.stderr)
        assert not p.stderr, (name,p.stderr)
        outputs.append(p.stdout); times[name].append(elapsed)
        print(name,run, f'{elapsed:.6f}',hashlib.sha256(p.stdout).hexdigest(),flush=True)
assert all(x == outputs[0] for x in outputs)
for name, vals in times.items(): print(name,'median',statistics.median(vals),'range',min(vals),max(vals))
print('all stdout bytes identical',len(outputs[0]))
