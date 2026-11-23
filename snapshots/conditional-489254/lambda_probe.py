#!/usr/bin/env python3
"""Scalar arithmetic probe only; assumes the cited graph-bound premises."""
from fractions import Fraction as F
U = F(163309458029, 1250000000000)
p = F(13889747654797, 3185049600000000)
def score(lam):
    assert F(3, 8) <= lam <= 1
    r = 1 + 9 * max(F(0), 1 - 2 * lam) ** 2 / (16 * lam * (3 - 2 * lam))
    return 1 + 1 / (2 * r * (U - (1-lam)*p))
old, new, target = F(35,71), F(24627,50000), F(244627,50000)
best=max((score(F(k,100000)),F(k,100000)) for k in range(48000,50001))
assert best == (score(new),new)
assert score(new)>target>F(489253,100000)
print('source: local 4.89253 note; mathematical premises NOT verified')
print('old',old,'score',float(score(old)))
print('new',new,'exact_score',score(new),'score',float(score(new)))
print('candidate',target,'exact_slack',score(new)-target,'slack',float(score(new)-target))
print('grid: 2001 points; no global optimality claim')
