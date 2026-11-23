"""Finite cubic-tree Gaussian wave and exact rational soft-tree optimizer.

Depth counts edges from root: depth 7 has 190 scored vertices and 192
unscored boundary leaves. Every internal vertex has all three incident edges;
leaves have no cost. This free boundary is NOT an infinite-volume optimum.
"""
from fractions import Fraction
from itertools import product
from collections import Counter
import numpy as np


def tree(depth):
    if not isinstance(depth, int) or depth < 1:
        raise ValueError('depth must be a positive integer')
    edges = []
    level = [0]
    internal = []
    nxt = 1
    for d in range(depth):
        new = []
        for v in level:
            internal.append(v)
            for _ in range(3 if d == 0 else 2):
                edges.append((v, nxt)); new.append(nxt); nxt += 1
        level = new
    return edges, internal


def sample_wave(depth, count, seed):
    """Sample spectral-edge invariant Gaussian wave (rows are iid)."""
    if not isinstance(count, int) or count < 0: raise ValueError('invalid count')
    edges, _ = tree(depth)
    rng = np.random.default_rng(seed)
    x = np.empty((count, len(edges)+1))
    x[:,0] = rng.normal(size=count)
    # Root: conditional variance 1/9; pair covariance -1/18.
    z = rng.normal(size=(count,3)); z -= z.mean(axis=1,keepdims=True)
    x[:,1:4] = (2*np.sqrt(2)/3)*x[:,0,None] + z/np.sqrt(6)
    parents = [-1]*(len(edges)+1)
    for p,c in edges: parents[c] = p
    for i in range(3,len(edges),2):
        p,c = edges[i]; p2,c2 = edges[i+1]
        assert p == p2
        mean = (2*np.sqrt(2)*x[:,p] - x[:,parents[p]])/2
        noise = rng.normal(size=count)/np.sqrt(12)
        x[:,c] = mean+noise; x[:,c2] = mean-noise
    return x


def _incidence(edges):
    adj = {}
    for i,(u,v) in enumerate(edges):
        adj.setdefault(u,[]).append((v,i)); adj.setdefault(v,[]).append((u,i))
    return adj


def _cost(bits, anchor, lam):
    return lam * (bits[0] != anchor) if len(set(bits)) == 1 else Fraction(1)


def evaluate(edges, anchors, bits, lam):
    lam = Fraction(lam)
    if len(bits) != len(edges) or any(b not in (0,1) for b in bits): raise ValueError('invalid edge bits')
    adj = _incidence(edges)
    return sum((_cost(tuple(bits[i] for _,i in adj[v]), a, lam) for v,a in anchors.items()), Fraction(0))


def solve(edges, anchors, lam):
    """Return (exact Fraction cost, edge-bit tuple), with free leaf boundary."""
    lam = Fraction(lam); adj = _incidence(edges)
    if not edges or len(adj) != len(edges)+1: raise ValueError('expected nonempty tree')
    if any(len(adj[v]) != 3 or a not in (0,1) for v,a in anchors.items()): raise ValueError('invalid anchors')
    if any(len(ns) != (3 if v in anchors else 1) for v,ns in adj.items()): raise ValueError('expected cubic internal vertices and boundary leaves')
    root = next(v for v in adj if len(adj[v]) == 1)
    decisions = {}
    visited = set()
    def visit(v, parent):
        if v in visited: raise ValueError('not a tree')
        visited.add(v)
        children = [(u,i) for u,i in adj[v] if u != parent]
        tables = [visit(u,v) for u,_ in children]
        values=[]
        for b in (0,1):
            candidates=[]
            for cb in product((0,1),repeat=len(children)):
                cost = sum((tab[x] for tab,x in zip(tables,cb)),Fraction(0))
                if v in anchors: cost += _cost((b,)+cb,anchors[v],lam)
                candidates.append((cost,cb))
            best = min(candidates); values.append(best[0]); decisions[v,b] = best[1]
        return values
    node, edge = adj[root][0]; vals=visit(node,root)
    if len(visited) != len(adj)-1: raise ValueError('not a connected tree')
    bit = min((vals[b],b) for b in (0,1))[1]
    result=[0]*len(edges); result[edge]=bit
    def recover(v,parent,b):
        children=[(u,i) for u,i in adj[v] if u != parent]
        for (u,i),x in zip(children,decisions[v,b]):
            result[i]=x; recover(u,v,x)
    recover(node,root,bit)
    return vals[bit],tuple(result)


def compare(edges, anchors, rule_bits, optimal_bits, lam, root=0):
    """Signed local/global cost differences and edge-disagreement components.

    Components share a vertex; this is descriptive topology, not causal attribution.
    Global gap is nonnegative only when optimal_bits is in fact globally optimal.
    """
    lam=Fraction(lam); adj=_incidence(edges)
    def vertex_cost(v,bits):
        return _cost(tuple(bits[i] for _,i in adj[v]),anchors[v],lam)
    gap = evaluate(edges,anchors,rule_bits,lam)-evaluate(edges,anchors,optimal_bits,lam)
    remaining={i for i,(a,b) in enumerate(zip(rule_bits,optimal_bits)) if a != b}
    components=[]
    while remaining:
        i=remaining.pop(); stack=[i]; size=0
        while stack:
            j=stack.pop(); size+=1
            for v in edges[j]:
                for _,k in adj[v]:
                    if k in remaining: remaining.remove(k); stack.append(k)
        components.append(size)
    return {'root_gap':vertex_cost(root,rule_bits)-vertex_cost(root,optimal_bits),
            'global_gap':gap, 'global_gap_per_vertex':gap/len(anchors),
            'disagreement_components':sorted(components,reverse=True)}


def run_experiment(rule, depth=7, count=10000, seed=20261123, lam=Fraction(35,71)):
    """Integrate actual rule(edges, anchors, wave_row)->edge bits; no surrogate.

    Independent realization is the sampling unit. Root mean is unbiased for the
    finite-depth rooted procedure, not an infinite-volume global objective. The
    global mean weights all internal vertices, most adjacent to the free boundary.
    Both summaries compare to the *same* globally optimal assignment; local gaps
    may be negative. MC standard errors use independent sample realizations.
    """
    if not callable(rule) or count < 2: raise ValueError('provide a rule and at least two samples')
    edges, vertices=tree(depth); waves=sample_wave(depth,count,seed)
    root=[]; global_=[]; hist=Counter(); positive=0
    for x in waves:
        anchors={v:int(x[v] >= 0) for v in vertices}
        _, optimum=solve(edges,anchors,lam)
        bits=tuple(rule(edges,anchors,x))
        result=compare(edges,anchors,bits,optimum,lam)
        if result['global_gap'] < 0: raise AssertionError('rule beat exact DP')
        root.append(float(result['root_gap'])); global_.append(float(result['global_gap_per_vertex']))
        hist.update(result['disagreement_components']); positive += result['global_gap'] > 0
    def summary(x):
        x=np.asarray(x); return {'mean':float(x.mean()),'standard_error':float(x.std(ddof=1)/np.sqrt(len(x)))}
    return {'count':count,'depth':depth,'seed':seed,'lambda':str(Fraction(lam)),
            'root_gap':summary(root),'global_gap_per_vertex':summary(global_),
            'positive_global_gap_samples':positive,'disagreement_component_size_counts':dict(sorted(hist.items())),
            'boundary':'unscored free leaves; root statistic is finite-depth only',
            'topology':'edge-disagreement components are descriptive, not causal'}
