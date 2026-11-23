# CircuitBreaker research commons

A shared evidence-first research project, separate from the Yukon challenge checkout and upstream PR. The repository coordinates independent attempts; it does not itself submit to Yukon or establish a mathematical result.

Read `RESEARCH_CONTRACT.md`, `agents/INDEPENDENT_AGENTS.md`, `SCOREBOARD.json`, and `evidence/LEDGER.md`. Run `python3 -m unittest discover -s tests -v` and `python3 validate.py`. Research findings and their limits are in `evidence/experiments/` and `evidence/counterexamples/`.

## Baseline boundary

`b346dab1-fa52-461c-a35b-fd811f712a31` is a Yukon submission ID, not a Git commit. At the recorded read it was validating with null official score, judgment, submitted commit and evaluated commit. Its note claims 4.89253; this is not a validated result. Its exact submitted bytes were not available. Do not treat a mutable challenge checkout as the frozen submission. See `evidence/LEDGER.md` and the captured Yukon response. On arrival of the immutable artifact and provenance, create `baseline/b346dab1/` containing every submission file, certificate and SHA-256 manifest and cross-check original bytes.

## Work lanes

Use separate worktrees/branches `research/hermes` and `research/antigravity`; share evidence promptly through reviewed commits and push only the named collaboration repo. Do not overwrite another lane, force-push, merge your own candidate, or submit to Yukon. The independent-attempt comparison requires each agent to freeze an attempt before consuming the other's new results; any prior exposure must be disclosed. Never describe separate branches or models as proof of independence.

The branch watcher is a read-only notification instrument in `tools/watch.py`; it does not adjudicate, merge or execute peer code. A notification is not a review. Its local journal is authoritative when delivery is interrupted.

## Verification limits

The bookkeeping validator checks snapshot hashes, structural integrity and declared review relationships. It cannot authenticate researchers, establish true independence, or verify mathematical claims. External review status and mathematical review status remain distinct.
