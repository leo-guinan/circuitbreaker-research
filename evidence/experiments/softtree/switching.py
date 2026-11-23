"""Conservative finite-window implementation of proof.md 112--128.

apply(edges, signs, lam=Fraction(35,71)) accepts a connected finite tree,
with vertices of degree at most 3 and nonzero signed numerical scores.
Signs are scores' signs; magnitudes are unnecessary because the guard-pair
criterion is symmetric. Unknown missing incident edges are NOT assumed absent:
any crossing component touching degree < 3 is unresolved and never switched;
a guard whose required continuation touches the boundary is unknown. The
finite-window cover on unresolved components is only a valid local fallback,
not a claim about the infinite-tree canonical cover. Costs are reported only
at degree-three vertices. The labels/cover are valid for all observed edges.
"""
from fractions import Fraction
from collections import deque


def _graph(edges, signs):
    edges = list(edges)
    adj = {v: [] for v in signs}
    seen = set()
    for i, (a, b) in enumerate(edges):
        if a not in adj or b not in adj or a == b or frozenset((a,b)) in seen:
            raise ValueError('invalid edge')
        seen.add(frozenset((a,b)))
        adj[a].append((b,i)); adj[b].append((a,i))
    if not adj or any(not s for s in signs.values()) or any(len(x)>3 for x in adj.values()):
        raise ValueError('nonzero scores and maximum degree three required')
    visited = set(); queue = [next(iter(adj))]
    while queue:
        v = queue.pop()
        if v not in visited:
            visited.add(v); queue.extend(w for w,_ in adj[v] if w not in visited)
    if len(visited) != len(adj) or len(edges) != len(adj)-1:
        raise ValueError('expected a connected tree')
    return edges, adj, {v: 1 if s > 0 else -1 for v,s in signs.items()}


def _arm(adj, s, parent, v):
    # Number of further crossing edges after the first crossing child.
    count = 0
    while True:
        if len(adj[v]) != 3:
            return None
        children = [w for w,_ in adj[v] if w != parent and s[w] != s[v]]
        if len(children) > 1:
            raise ValueError('crossing degree exceeds two')
        if not children:
            return count
        parent, v = v, children[0]
        count += 1


def _guard(adj, s, parent, v):
    if s[parent] != s[v]:
        raise ValueError('guard requires same-sign parent')
    if len(adj[v]) != 3:
        return 'unknown'
    children = [w for w,_ in adj[v] if w != parent]
    neg = [w for w in children if s[w] != s[v]]
    if not neg:
        return 'U'
    arms = [_arm(adj,s,v,w) for w in neg]
    if any(x is None for x in arms):
        return 'unknown'
    if len(neg) == 2:
        return 'W2' if all(x % 2 for x in arms) else 'other'
    if arms[0] % 2:
        return 'W1'
    same = next(w for w in children if w != neg[0])
    g = _guard(adj,s,v,same)
    if g in ('U','W1','W2'):
        return 'Vodd'
    return 'unknown' if g == 'unknown' else 'other'


def guard(edges, signs, parent, vertex):
    """Guard relative to parent, with sign symmetry; unknown is conservative."""
    _, adj, s = _graph(edges, signs)
    if parent not in [w for w,_ in adj[vertex]]:
        raise ValueError('parent is not adjacent')
    return _guard(adj,s,parent,vertex)


def apply(edges, signs, lam=Fraction(35,71)):
    """Return observed cover/labels/costs and explicit truncation diagnostics."""
    edges, adj, s = _graph(edges,signs)
    if not 0 <= lam <= 1:
        raise ValueError('lambda must lie in [0,1]')
    cross = {v:[w for w,_ in adj[v] if s[v]!=s[w]] for v in adj}
    if any(len(ns)>2 for ns in cross.values()):
        raise ValueError('crossing degree exceeds two')
    seen=set(); cover=set(); components=[]; unresolved=0
    for start in adj:
        if not cross[start] or start in seen:
            continue
        stack=[start]; component=set()
        while stack:
            v=stack.pop()
            if v in component: continue
            component.add(v); stack.extend(cross[v])
        seen |= component
        endpoint=next(v for v in component if len(cross[v])==1)
        path=[endpoint]; prev=None
        while True:
            nxt=[w for w in cross[path[-1]] if w != prev]
            if not nxt: break
            prev=path[-1]; path.append(nxt[0])
        n=len(path)-1
        if n%2:
            if s[path[0]]<0: path.reverse()
            chosen=path[::2]
        else:
            chosen=path[1::2]
        cover.update(chosen)
        complete=all(len(adj[v])==3 for v in (path[0],path[-1]))
        if not complete: unresolved+=1
        components.append((path,complete))
    base=set(cover); switched=0; boundaries=set(); unknown_guards=0
    OUT={'U','W1','W2'}
    for path,complete in components:
        n=len(path)-1
        if n%2==0 or not complete: continue
        r=0
        for j in range(0,n,2):
            u=path[j]
            off=[w for w,_ in adj[u] if w not in path]
            if len(adj[u])!=3 or len(off)!=(2 if j==0 else 1):
                unknown_guards+=1; break
            gs=[_guard(adj,s,u,w) for w in off]
            unknown_guards+=sum(g=='unknown' for g in gs)
            admitted=(all(g in OUT|{'Vodd'} for g in gs) and any(g in OUT for g in gs)) if j==0 else gs[0] in OUT
            if not admitted: break
            r+=1
        for k in range(r):
            cover.remove(path[2*k]); cover.add(path[2*k+1])
        switched+=r
        if r and 2*r<n:
            boundaries.add(frozenset((path[2*r-1],path[2*r])))
    labels=[]
    for a,b in edges:
        if s[a]!=s[b]:
            if a not in cover and b not in cover: raise AssertionError('invalid cover')
            if a in cover and b in cover:
                if frozenset((a,b)) not in boundaries: raise AssertionError('unexpected double cover')
                labels.append(-1)
            else:
                labels.append(s[b] if a in cover else s[a])
        else:
            labels.append(-s[a] if a in cover and b in cover else s[a])
    costs={}
    for v,inc in adj.items():
        if len(inc)==3:
            vals={labels[i] for _,i in inc}
            costs[v] = 1 if len(vals)>1 else (lam if next(iter(vals))!=s[v] else 0)
    return {'cover':cover,'base_cover':base,'labels':labels,'costs':costs,
            'switches':switched,'unresolved_paths':unresolved,
            'unknown_guards':unknown_guards,'valid_cover':True,
            'boundary_edges':boundaries,
            'boundary_vertices':{v for v in adj if len(adj[v])<3},
            # Every finite tree has a boundary; unobserved same-sign edges and
            # their remote crossing components can affect the global cover.
            'canonical_complete':False}
