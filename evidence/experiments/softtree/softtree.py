"""Finite degree-three trees; all scores are doubled (lambda = 1/2)."""
from itertools import product

def solve(edges, anchors):
    adj={}
    for i,(u,v) in enumerate(edges):
        adj.setdefault(u,[]).append((v,i)); adj.setdefault(v,[]).append((u,i))
    assert len(edges)==len(adj)-1 and edges
    assert all(len(adj[v])==3 for v in anchors)
    assert all((len(n)==3)==(v in anchors) for v,n in adj.items())
    n=len(edges)
    def visit(v,parent):
        children=[(w,i) for w,i in adj[v] if w!=parent]
        tables=[(i,visit(w,v)) for w,i in children]
        out={}
        for parentbit in (0,1):
            candidates=[]
            for cbits in product((0,1),repeat=len(children)):
                cost=0; assignment=[-1]*n
                for (i,tab),bit in zip(tables,cbits):
                    c,sub=tab[bit]; cost+=c; assignment[i]=bit
                    for j,x in enumerate(sub):
                        if x!=-1: assignment[j]=x
                if v in anchors:
                    values=(parentbit,)+cbits
                    cost+=2 if len(set(values))>1 else int(values[0]!=anchors[v])
                candidates.append((cost,tuple(assignment)))
            out[parentbit]=min(candidates)
        return out
    root=next(v for v,ns in adj.items() if len(ns)==1)
    w,i=adj[root][0]; table=visit(w,root)
    candidates=[]
    for bit in (0,1):
        cost,assignment=table[bit]; a=list(assignment); a[i]=bit
        candidates.append((cost,tuple(a)))
    return min(candidates)

def brute(edges, anchors):
    # Independent vertex-centric evaluation over all 2^|E| configurations.
    incidence={v:[i for i,(a,b) in enumerate(edges) if v==a or v==b] for v in anchors}
    best=None
    for bits in product((0,1), repeat=len(edges)):
        c=0
        for v,inds in incidence.items():
            x,y,z=(bits[i] for i in inds)
            c += 2 if not x==y==z else int(x!=anchors[v])
        item=(c,bits)
        if best is None or item<best: best=item
    return best

def local(edges, anchors):
    def score(bits):
        total=0
        for v,a in anchors.items():
            vals=[bits[i] for i,(u,w) in enumerate(edges) if v==u or v==w]
            total += 2 if len(set(vals))>1 else int(vals[0]!=a)
        return total
    results=[]
    for start in (0,1):
        b=[start]*len(edges); c=score(b)
        while True:
            # First strictly improving edge in index order; restart scan.
            for i in range(len(b)):
                b[i]^=1; candidate=score(b)
                if candidate<c:
                    c=candidate; break
                b[i]^=1
            else: break
        results.append((c,tuple(b)))
    return min(results)
