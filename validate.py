#!/usr/bin/env python3
"""Validate research records and actual snapshot files; no network access."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEX = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
RESEARCH = {"idea", "in_progress", "candidate", "reviewed", "refuted"}
REVIEW = {"not_requested", "pending", "approved", "changes_requested"}
EXTERNAL = {"not_submitted", "validating", "accepted", "rejected", "unknown"}


def digest(manifest):
    return hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate(root):
    root = Path(root)
    errors = []
    def need(condition, message):
        if not condition:
            errors.append(message)
    try:
        reg = json.loads((root / 'REGISTRY.json').read_text())
        board = json.loads((root / 'SCOREBOARD.json').read_text())
        if reg.get('version') != 1 or board.get('version') != 1:
            return ['unsupported schema version']
        agents, entries = reg['agents'], board['entries']
        if not isinstance(agents, list) or not isinstance(entries, list):
            return ['agents and entries must be arrays']
        agent_ids = [a['id'] for a in agents]
        ids = [e['id'] for e in entries]
        if any(not isinstance(i, str) or not ID.fullmatch(i) for i in agent_ids + ids):
            return ['invalid identifier']
        if len(set(ids)) != len(ids) or len(set(agent_ids)) != len(agent_ids):
            return ['duplicate identifier']
        for a in agents:
            need(isinstance(a['name'], str) and bool(a['name'].strip()), 'agent name required')
        by_id = {e['id']: e for e in entries}
        for e in entries:
            i = e['id']
            authors = e['authors']
            deps = e['dependencies']
            reviews = e['reviews']
            if not all(isinstance(x, list) for x in (authors, deps, reviews)):
                errors.append(f'{i}: authors, dependencies and reviews must be arrays'); continue
            need(bool(authors) and all(a in agent_ids for a in authors), f'{i}: unknown or missing author')
            need(len(set(deps)) == len(deps) and all(d in by_id and d != i for d in deps), f'{i}: invalid dependencies')
            need(e['research_status'] in RESEARCH, f'{i}: invalid research status')
            need(e['review_status'] in REVIEW, f'{i}: invalid review status')
            need(e['external_status'] in EXTERNAL, f'{i}: invalid external status')
            need(isinstance(e['claim'], str) and bool(e['claim'].strip()), f'{i}: claim required')
            need(isinstance(e['evidence'], list) and bool(e['evidence']) and all(isinstance(x, str) and x.strip() for x in e['evidence']), f'{i}: evidence required')
            manifest = e['snapshot']['files']
            need(isinstance(manifest, dict) and bool(manifest), f'{i}: snapshot must have files')
            if not isinstance(manifest, dict): continue
            folder = root / 'snapshots' / i
            if folder.is_symlink() or not folder.is_dir():
                errors.append(f'{i}: snapshot directory missing or symlink'); continue
            actual = set()
            for p in folder.rglob('*'):
                if p.is_symlink(): errors.append(f'{i}: symlink prohibited'); continue
                if p.is_file(): actual.add(p.relative_to(folder).as_posix())
            need(actual == set(manifest), f'{i}: snapshot manifest differs from files')
            for rel, sha in manifest.items():
                p = folder / rel
                safe = isinstance(rel, str) and not rel.startswith('/') and all(x not in ('..', '.', '') for x in rel.split('/'))
                need(safe and isinstance(sha, str) and bool(HEX.fullmatch(sha)), f'{i}: invalid snapshot manifest')
                if safe and p.is_file() and not any((folder.joinpath(*rel.split('/')[:j])).is_symlink() for j in range(1, len(rel.split('/')) + 1)):
                    need(hashlib.sha256(p.read_bytes()).hexdigest() == sha, f'{i}: snapshot hash mismatch {rel}')
            sd = digest(manifest)
            need(e['snapshot']['digest'] == sd, f'{i}: snapshot digest mismatch')
            approvals = []
            for r in reviews:
                need(r['reviewer'] in agent_ids and r['reviewer'] not in authors, f'{i}: self or unknown review')
                need(r['verdict'] in {'approved', 'changes_requested'}, f'{i}: invalid verdict')
                need(r['snapshot_digest'] == sd, f'{i}: stale review')
                need(isinstance(r['evidence'], str) and bool(r['evidence'].strip()), f'{i}: review evidence required')
                if r['verdict'] == 'approved' and r['reviewer'] in agent_ids and r['reviewer'] not in authors and r['snapshot_digest'] == sd:
                    approvals.append(r)
            need(e['review_status'] != 'approved' or bool(approvals), f'{i}: approval needs independent review')
            need(e['research_status'] != 'reviewed' or e['review_status'] == 'approved', f'{i}: reviewed needs approval')
        visiting, done = set(), set()
        def visit(i):
            if i in visiting: errors.append(f'{i}: dependency cycle'); return
            if i in done: return
            visiting.add(i)
            for d in by_id[i]['dependencies']:
                if d in by_id: visit(d)
            visiting.remove(i); done.add(i)
        for i in ids: visit(i)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
        errors.append(f'invalid input: {exc}')
    return errors


if __name__ == '__main__':
    failures = validate(ROOT)
    print('\n'.join(failures) if failures else 'Research records valid (not a mathematical verification).')
    raise SystemExit(bool(failures))
