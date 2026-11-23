# Evidence ledger

## Yukon candidate observation (read only)

- Retrieval: `yukon submissions --all --json` in the active challenge directory; local observation on 2026-11-23. The returned set contained 484 submissions. `evidence/yukon-b346dab1.json` preserves the selected complete response record verbatim as JSON (formatting normalized). It is a point-in-time API observation, not an immutable candidate artifact or a mathematical review.
- Benchmark: `737d32c6-440f-4a31-8bde-5fca240ba58e`; submission `b346dab1-fa52-461c-a35b-fd811f712a31`; status `validating`; official score, judgment, evaluation, submitted commit and evaluated commit all null. Its public note contains 4.89253, a claim only. No official or independent acceptance is implied.
- Separate local source checkout: HEAD `fa66419a11ce279cda692a13796f5532afd754e1`, with staged and unstaged modifications to submission files, inspected read-only. `b346dab1` is not an object in that Git repository. No candidate files were copied, because their equivalence to submitted bytes is unproven. Harness HEAD is not the candidate snapshot.
- Next evidence required: fetch exact immutable submitted artifact or evaluated commit, compare per-file cryptographic hashes to Yukon intake/evidence, record the completed evaluation and dependencies, then independently verify. Recheck Yukon status; the captured response may become stale.

## Later readback and reproducibility

Yukon subsequently rejected submission `b346dab1-fa52-461c-a35b-fd811f712a31`: the recorded primary decision says both hosted certificate runs timed out with exit code -9 and no result. This is an evidence failure, not a disproof. The immutable submitted and evaluated Git commit is `51bd01f184d39d2105a2764df51bf57792b300e9`, separate from harness source `fa66419a11ce279cda692a13796f5532afd754e1`. The six files recovered from that commit are stored at `baseline/b346dab1/` with SHA-256 manifest; their bytes matched the observed active local checkout at retrieval, but the commit is the provenance anchor. `evidence/b346dab1-rejection.json` is the later readback and preserves the stated objection.

A local replay of those exact recovered bytes using `python3 -I -B certify.py` completed in 9.62 seconds on the investigator's machine and emitted the expected JSON. This confirms local completion, not timing on the hosted worker and not the mathematical proof. The initial `validating` status above is a historical observation. Model label in the submitted note is submitter-declared metadata, not evidence of which model generated any particular proof section.

## Local commons tests
The repository's schema and integrity tests concern collaboration bookkeeping only. They do not verify any circuit lower bound, external result, or reviewer independence in reality.
