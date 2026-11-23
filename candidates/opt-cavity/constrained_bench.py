#!/usr/bin/env python3
"""Compare original and candidate in pinned Docker; emulated host is not Yukon."""
import hashlib,json,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parents[2]
image='python:3.12.12-slim-bookworm@sha256:2986c55feb36e6cae00fa1fefb454283e4b33f35e75ff8bdd123b134130be301'
paths={'baseline':root/'baseline/b346dab1','candidate':root/'candidates/opt-cavity'}
results=[]
for idx,name in enumerate(['baseline','candidate','candidate','baseline']):
 path=paths[name]
 cmd=['docker','run','--rm','--platform','linux/amd64','--network','none','--cpus','1','--memory','256m','--memory-swap','256m','--pids-limit','32','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','-v',f'{path}:/snapshot/files:ro','--entrypoint','/usr/bin/timeout',image,'20s','/usr/local/bin/python3','-I','-B','/snapshot/files/certify.py']
 start=time.monotonic(); p=subprocess.run(cmd,capture_output=True,timeout=80);elapsed=time.monotonic()-start
 results.append({'run':idx,'variant':name,'exit_code':p.returncode,'host_wall_s':elapsed,'stdout_bytes':len(p.stdout),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_bytes':len(p.stderr)})
 print(json.dumps(results[-1]),flush=True)
out={'image':image,'platform':'linux/amd64 on Apple Silicon Docker emulation; not hosted CPU','cpu_limit':1,'memory_mb':256,'memory_swap_mb':256,'inside_process_wall_timeout_s':20,'host_wall_includes_container_startup':True,'results':results,'limitations':['not exact verifier snapshot/setup timer','shared machine contention not controlled','no result bytes on timeout']}
(root/'candidates/opt-cavity/docker_receipt.json').write_text(json.dumps(out,indent=2)+'\n')
