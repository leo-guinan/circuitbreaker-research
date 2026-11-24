#!/usr/bin/env python3
"""Poll a single Git branch; emit JSON only on changes. Never executes repository code."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

GIT = '/usr/bin/git'
ENV = {'PATH': '/usr/bin:/bin', 'HOME': '/nonexistent', 'GIT_CONFIG_NOSYSTEM': '1',
       'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_TERMINAL_PROMPT': '0',
       'GIT_ASKPASS': '/usr/bin/false', 'SSH_ASKPASS': '/usr/bin/false',
       'GIT_OPTIONAL_LOCKS': '0', 'LC_ALL': 'C'}
OID = re.compile(r'^[0-9a-f]{40}(?:[0-9a-f]{24})?$')

class WatchError(Exception):
    def __init__(self, message, stage='validation', error_class='watch_error', exit_code=None):
        super().__init__(message)
        self.stage = stage
        self.error_class = error_class
        self.exit_code = exit_code

def git(*args, cwd=None, check=True, stage='git'):
    try:
        r = subprocess.run([GIT, '-c', 'core.hooksPath=/dev/null', '-c', 'credential.helper=',
                            '-c', 'gc.auto=0', '-c', 'maintenance.auto=false',
                            '-c', 'protocol.ext.allow=never', *args], cwd=cwd, env=ENV,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    except subprocess.TimeoutExpired:
        raise WatchError('git timed out', stage, 'git_timeout') from None
    except OSError:
        raise WatchError('git invocation failed', stage, 'git_oserror') from None
    if check and r.returncode:
        # Never print remote, git diagnostics, local configuration or credentials.
        raise WatchError('git operation failed', stage, 'git_exit', r.returncode)
    return r

def atomic_json(path, obj):
    data = (json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(',', ':')) + '\n').encode()
    fd, name = tempfile.mkstemp(prefix='.state-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
        d = os.open(str(path.parent), os.O_RDONLY)
        try: os.fsync(d)
        finally: os.close(d)
    finally:
        if os.path.exists(name): os.unlink(name)

def validate_remote(remote):
    if remote.startswith('/'):
        return
    u = urlsplit(remote)
    if u.scheme != 'https' or not u.hostname or u.username or u.password or u.query or u.fragment:
        raise WatchError('remote must be an absolute local path or credential-free HTTPS URL')

def poll(remote, branch, root):
    validate_remote(remote)
    if not branch or branch.startswith('-') or git('check-ref-format', 'refs/heads/' + branch, check=False).returncode:
        raise WatchError('invalid branch name')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(root, 0o700)
    with open(root / 'lock', 'a+b') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: return None
        state_path = root / 'state.json'
        if state_path.exists():
            try: state = json.loads(state_path.read_text())
            except (OSError, ValueError): raise WatchError('invalid state file') from None
            if state.get('remote') != remote or state.get('branch') != branch:
                raise WatchError('state belongs to a different remote or branch')
        else:
            state = {'version': 1, 'remote': remote, 'branch': branch, 'tip': None,
                     'present': False, 'initialized': False, 'events': []}
        repo = root / 'objects.git'
        if not repo.exists(): git('init', '--bare', '--quiet', str(repo), stage='repository_init')
        ref = 'refs/heads/' + branch
        result = git('ls-remote', '--heads', '--', remote, ref, stage='remote_lookup').stdout.splitlines()
        if len(result) > 1: raise WatchError('ambiguous remote branch response')
        if not result:
            if not state['initialized'] or not state['present']:
                return None
            event = {'kind': 'branch_missing', 'previous_tip': state['tip'], 'tip': None, 'commits': []}
            state['present'] = False
        else:
            fields = result[0].split(b'\t')
            if len(fields) != 2 or fields[1] != ref.encode() or not OID.fullmatch(fields[0].decode('ascii', 'replace')):
                raise WatchError('invalid remote branch response')
            # Fetch by ref, not the advertised oid: validate fetched oid, tolerate branch races by retrying later.
            git('-C', str(repo), '-c', 'fetch.fsckObjects=true', 'fetch', '--no-tags', '--no-recurse-submodules',
                '--force', '--', remote, '+' + ref + ':refs/watch/target', stage='remote_fetch')
            tip = git('-C', str(repo), 'rev-parse', '--verify', 'refs/watch/target^{commit}', stage='resolve_tip').stdout.decode().strip()
            if tip != fields[0].decode(): raise WatchError('branch changed during fetch; retry')
            # Keep every observed tip reachable even after force pushes or explicit GC.
            git('-C', str(repo), 'update-ref', 'refs/watch/archive/' + tip, tip, stage='archive_tip')
            if not state['initialized']:
                state.update(initialized=True, present=True, tip=tip)
                atomic_json(state_path, state)
                return None
            old = state['tip']
            if state['present'] and old == tip: return None
            if old == tip:
                commits = []; kind = 'branch_restored'
            else:
                commits = git('-C', str(repo), 'rev-list', '--reverse', '--topo-order', tip, '^' + old, stage='list_commits').stdout.decode().splitlines()
                if any(not OID.fullmatch(c) for c in commits): raise WatchError('invalid commit list')
                kind = 'branch_updated' if state['present'] else 'branch_restored'
            event = {'kind': kind, 'previous_tip': old, 'tip': tip, 'commits': commits}
            state.update(present=True, tip=tip)
        event['sequence'] = len(state['events']) + 1
        state['events'].append(event)
        # Commit durable journal + cursor together, then emit. Journal is the authoritative outbox;
        # stdout may be lost if the process crashes after this write.
        atomic_json(state_path, state)
        return event

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--remote', required=True); p.add_argument('--branch', required=True)
    p.add_argument('--state-dir', required=True)
    a = p.parse_args()
    try:
        event = poll(a.remote, a.branch, Path(a.state_dir).expanduser().resolve())
        if event is not None: print(json.dumps(event, sort_keys=True), flush=True)
    except (WatchError, OSError, ValueError, KeyError, TypeError) as exc:
        detail = {'status': 'watch_failed', 'stage': getattr(exc, 'stage', 'state_or_protocol'),
                  'error_class': getattr(exc, 'error_class', type(exc).__name__),
                  'cursor_status': 'unknown_check_state'}
        if isinstance(exc, WatchError) and exc.exit_code is not None:
            detail['exit_code'] = exc.exit_code
        print(json.dumps(detail, sort_keys=True), file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__': sys.exit(main())
