# CircuitBreaker research commons

An independent **local** collaboration repository, not a challenge clone or a submission mechanism. The active challenge checkout at `/Users/leoguinan/hack-personal/circuitbreaker` is outside this repository and must not be edited by commons agents. No push, public posting, scheduling, or submission is authorized by this repository.

Start with `RESEARCH_CONTRACT.md`, `agents/INDEPENDENT_AGENTS.md`, `REGISTRY.json`, and `SCOREBOARD.json`. Run `python3 -m unittest discover -s tests -v` and `python3 validate.py` before sharing results. `evidence/LEDGER.md` records observations and their limits. Branches/worktrees isolate work, not identities; a reviewer must be independent of all authors and must attest to the exact immutable snapshot.

## Baseline boundary
`b346dab1-fa52-461c-a35b-fd811f712a31` is a **Yukon submission ID**, not a Git commit. At the recorded read it was `validating`, with null official score, evaluation, and submission/evaluated commit. Its note mentions 4.89253; neither a result nor exact submitted bytes were available. The current dirty challenge checkout is not the frozen submission. Do not inherit or assert the score as validated. The pinned harness source `fa66419a11ce279cda692a13796f5532afd754e1` is separate from candidate content. See `evidence/LEDGER.md` and the captured Yukon response.

## Snapshot workflow
Only import a candidate when its immutable source and original exact bytes can be independently tied to its submission/evaluation. Place files under `snapshots/<id>/`, declare SHA-256 per file in the scoreboard and record origin in the ledger. Git commits provide history; the validator checks content on every run, including uncommitted changes. Never copy the live dirty tree and label it the evaluated snapshot. Dependencies must name earlier registered entries, form an acyclic graph, and be credited even when unvalidated. Reviews must target the snapshot digest and be recorded separately from claims and external statuses.
