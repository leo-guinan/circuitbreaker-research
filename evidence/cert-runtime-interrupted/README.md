# Interrupted exact-certificate optimization investigations

Two parallel exploratory workers were interrupted by HTTP 429 before delivering a final review. Their partial logs remain in this profile's delegation cache. Treat these as experiment records, not independently reproduced improvements.

## Measurements recovered

- Worker 1 profiled the unmodified Python 3.11 certificate: 12,821,690 calls to `lmlo`, 5,953,906 calls to `geo_interp`, and 66,046,322 calls to `math.isqrt` in one run. Python profiling adds overhead. The preserved source profile is `profile-original.txt`.
- Worker 2 tried an LRU cache of 262,144 `lmlo` entries. Its measured complete certificate took 12.28 s, with 2,917,289 hits and 9,904,401 misses. Caching at a different level took 11.13 s with 327,022 hits and 5,626,884 misses. These were separate probes, not controlled paired benchmarks. Neither establishes useful acceleration; the cache increases memory pressure.
- An exploratory PyPy interpreter run produced the expected cavity integer tuple; three calls in one process took 7.612, 5.775, and 5.741 s. These are warmed-process measurements, not valid cold CPython 3.12 hosted timings; PyPy is not the configured hosted interpreter.
- The Cython full-module compile timed out after 300 s without a completed extension. It is not a runnable certificate. In addition, the configured pinned Python image exposes `ctypes` but no `cc`, `gcc`, `clang`, or `make` on PATH, so runtime compilation there cannot be assumed. Vendoring a compiled component would require its own portability, source-verification and challenge-policy review; it is not an accepted solution.

## Current status

None of these approaches reaches the cold local sub-five-second target or demonstrates a host-compliant result. The candidate in `../../candidates/opt-cavity/` and frozen original in `../../baseline/b346dab1/` remain distinct. No theorem or numerical certificate is independently proven by profiling. Further changes need exact-output differential testing, genuine cold-run measurements and an independent proof review before submission.
