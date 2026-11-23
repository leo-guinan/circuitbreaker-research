# Rejected timeout experiment — unpromoted candidate

Baseline: Yukon submission b346dab1-fa52-461c-a35b-fd811f712a31, evaluated commit 51bd01f184d39d2105a2764df51bf57792b300e9. The six frozen original files are in `../../baseline/b346dab1/`, with their own manifest. This directory is a separate candidate, not the original submission.

The hosted evaluator rejected the claim because both initial and follow-up certificate runs timed out and yielded no numerical evidence. The archived GitHub Actions run is 45270375011 in the upstream verifier repository. The verifier uses a 20-second wall-clock budget, 1 CPU, 256 MiB memory and swap combined, Python 3.12.12 linux/amd64. The timer starts before snapshot preparation and Docker image inspection, so runtime alone cannot consume the entire budget. Image preparation in the outer workflow occurs before the timed experiment. Host CPU model, actual memory usage and actual CPU consumption are unknown; `-9` by itself is not proof of OOM. Timeout is not a disproof.

## Candidate and negative result

The candidate only reuses a value where already-computed bounds are identical; it does not replace exact arithmetic or change proof assumptions. Differential checks: `python3 -B -m unittest -v test_differential` — 3 tests passed (small grids and 20,000 randomized arithmetic comparisons). An independent worker reported alternating fresh interpreter runs: baseline median 9.934 s, candidate median 9.855 s; all six 697-byte outputs matched SHA-256 `cf56b80c1f199fd406e11fd16ea4ad374d1cf0b91f4897efc4819ea4209589d8`. The distributions overlap and do not establish a reliable improvement. The target below 5 s was not met.

## Constrained replay

From the repo root run `python3 -B candidates/opt-cavity/constrained_bench.py`. The recorded four alternating cold container invocations appear in `docker_receipt.json`. Both original runs and both candidate runs reached the 20-second in-container wall timeout (exit 124; no stdout). They use the pinned amd64 image on Apple Silicon emulation with 1 CPU, 256 MiB and swap=256 MiB. These are not native Yukon CPU timings, do not include the verifier's exact setup wrapper, and were run on a shared machine without controlled contention. Empty outputs are not evidence of identical numerical results in the container. The process deadline starts after container startup, whereas the actual verifier deadline includes setup.

Before any future submission: deliver substantial speed and memory headroom, repeat cold start on the native target architecture with the actual verifier, compare all result bytes, independently review the proof and loss of any caching/rounding bounds, and obtain explicit approval. No submission or external write was made.
