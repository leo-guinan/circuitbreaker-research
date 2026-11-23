import json, random
from itertools import product
from collections import Counter
from softtree import solve, brute, local

def tree(k):
    edges=[(0,1),(0,2),(0,3)]; leaves=[1,2,3]; nxt=4
    for _ in range(k-1):
        v=leaves.pop(0)
        edges.extend([(v,nxt),(v,nxt+1)]); leaves.extend((nxt,nxt+1)); nxt+=2
    anchors=sorted(set(v for e in edges for v in e)-set(leaves))
    return edges,anchors

def run():
    rng=random.Random(20261123); cases=[]; summaries=[]
    for k,count in ((1,2),(3,8),(5,32),(7,16),(15,64),(31,64)):
        edges,vertices=tree(k)
        # Enumerate every anchor assignment for k<=5, sample independently thereafter.
        samples=list(product((0,1),repeat=k)) if k<=5 else [tuple(rng.randrange(2) for _ in vertices) for _ in range(count)]
        gaps=[]
        for sample in samples:
            anchors=dict(zip(vertices,sample)); d=solve(edges,anchors); l=local(edges,anchors)
            b=brute(edges,anchors) if k<=7 else None
            assert b is None or d[0]==b[0]
            assert d[0]<=l[0]
            def pack(x): return None if x is None else {'cost2':x[0], 'edge_bits':list(x[1])}
            cases.append({'edges':edges,'anchors':anchors,'dp':pack(d),'brute':pack(b),'local':pack(l)})
            gaps.append(l[0]-d[0])
        summaries.append({'internal_vertices':k,'edges':len(edges),'cases':len(samples),'oracle_cases':len(samples) if k<=7 else 0,'local_worse':sum(g>0 for g in gaps),'gap2_histogram':dict(sorted(Counter(gaps).items()))})
    return {'seed':20261123,'weight_scale':2,'lambda':'1/2','baseline':'all-zero and all-one starts; first strict improving single-edge flip by edge index, restart scan, take lexicographic min (cost,bits); not switching-guard', 'summaries':summaries,'cases':cases}

if __name__=='__main__':
    result=run()
    with open('results.json','w') as f: json.dump(result,f,indent=2,sort_keys=True)
    print(json.dumps(result['summaries'],indent=2))
    for c in result['cases']:
        if c['local']['cost2']>c['dp']['cost2']:
            print('first_gap_witness:',json.dumps(c,sort_keys=True)); break
