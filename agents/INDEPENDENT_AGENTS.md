# Agent instructions

Read `RESEARCH_CONTRACT.md` first. Never modify another agent's worktree or the active challenge checkout. Use dedicated branches `research/hermes` and `research/antigravity`. Commit reproducible results with hypotheses, dependencies, commands, observations and limitations; share evidence through your own branch, not by silently overwriting shared artifacts. No force-push, Yukon submission, upstream PR, or external post without Leo's explicit approval.

## Antigravity: first handoff

1. Start from the shared baseline in `main`, work only in `research/antigravity`, and disclose previous exposure to Hermes's lambda and tree-DP work. This first exchange is not a blinded independent trial because both agents already have shared context.
2. Independently check the exact 4.89254 conditional rational candidate in `evidence/experiments/lambda_probe.py`: verify the proof's lambda range, dependence of all certificates, exact rational arithmetic, unchanged constraints and arbitrary-slack transfer. Try to falsify it. Arithmetic alone is not a full proof.
3. Inspect `evidence/experiments/softtree/`: its 10,000-sample DP experiment uses a free boundary and unresolved-path fallback. Determine whether a bounded local witness and exact event probability can replace the observed finite-tree gap. Do not claim the finite simulation proves an infinite bound.
4. Write `research/antigravity/outcomes/<unique-id>.md` with claim, source hashes and dependencies, reproducible commands, exact results, failed checks, review verdict and unresolved proof obligations. Commit and push ONLY `research/antigravity` to this collaboration repository. A branch watcher records new commits; it does not execute them, approve them or submit anything.
5. Request independent review from Hermes. Do not alter the immutable baseline or set your own outcome to independently mathematically reviewed.

## Hermes lane

Use `research/hermes` to explore structural tree-DP, counterexamples and finite, explicitly bounded candidate witnesses. Capture negative results and exact test receipts. Request Antigravity review of any new solution, with exact snapshot digest. Stop at the verification reserve; submit only after separate explicit authorization.
