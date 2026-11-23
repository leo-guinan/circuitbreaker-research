# Experiments and limits

## Conditional lambda candidate

`python3 -I -B evidence/experiments/lambda_probe.py` uses exact rational arithmetic and the U,p numbers in the b346dab1 public note. It finds lambda 24627/50000 and a limiting scalar coefficient about 4.892541607515938, leaving a strict margin for 4.89254. It is conditional on the unverified proof, certificate and transfer, and is not a Yukon submission or independently reviewed theorem. It uses the public note's parameters; dependency attribution is recorded in the scoreboard. A numerical checker does not supply the proof.

## Finite tree exploration

`cd evidence/experiments/softtree && python3 -B -m unittest -v` requires NumPy. `python3 -B experiment.py --depth 7 --count 10000 --seed 20261123 --out wave_results.json` regenerates the seeded result. The finite-window switching rule applies the proof's rule only to complete observed crossing paths; unfinished paths use an explicitly different finite cover and free leaves have no cost. The exact DP optimizes that finite objective at 35/71. These runs do not establish infinite-tree canonical behavior, realizable additional savings, a proof or Δp. Root-neighborhood group contributions are descriptive, not causal, and can depend on DP tie-breaking.

On the recorded execution 14 combined tests passed. The exact run recorded mean finite-window cost gap 0.07041902891030392 per scored vertex, standard error 0.0002174954058390636, 191737 unresolved crossing paths, and 77962 unknown guards across 10000 samples. These are observations of the bounded instrument, not circuit bounds.

## Restrictions counterexample

`python3 -B evidence/counterexamples/restriction.py` illustrates that restriction complexities cannot simply be added under unrestricted sharing. The exhaustive finite enumeration corroborates an elementary all-n parity proof. The finite enumeration is not itself an asymptotic proof.
