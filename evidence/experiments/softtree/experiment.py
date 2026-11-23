"""Finite-window switching vs exact free-boundary DP; not infinite-tree proof."""
import argparse, json, math
from collections import defaultdict
from fractions import Fraction
import numpy as np
from wave_dp import tree, sample_wave, solve, evaluate
from switching import apply

LAM = Fraction(35,71)
def wave_experiment(depth=7,count=10000,seed=20261123):
 edges, vertices = tree(depth)
 wave = sample_wave(depth,count,seed)
 neighbors={v:[] for v in range(len(edges)+1)}
 for a,b in edges: neighbors[a].append(b); neighbors[b].append(a)
 groups=defaultdict(lambda:{'count':0,'gap_numerator':0,'gap_samples':0,'root_gap_numerator':0,'root_gap_positive':0,'root_gap_negative':0})
 samples=[]; unresolved=unknown=switches=0
 for x in wave:
  signs={i:float(y) for i,y in enumerate(x)}
  anchors={v:int(x[v]>=0) for v in vertices}
  best,bits=solve(edges,anchors,LAM)
  out=apply(edges,signs,LAM)
  labels=tuple(int(v>0) for v in out['labels'])
  cost=evaluate(edges,anchors,labels,LAM)
  gap=cost-best
  assert gap >= 0 and gap.denominator in (1,71)
  gn=int(gap*71)
  def degree(v): return sum((x[v]>0)!=(x[w]>0) for w in neighbors[v])
  rootdeg=degree(0)
  near=sorted((int((x[0]>0)!=(x[w]>0)), degree(w)) for w in neighbors[0])
  key=f'root_cross={rootdeg};neighbors=' + ','.join(f'{a}:{b}' for a,b in near)
  g=groups[key]; g['count']+=1;g['gap_numerator']+=gn;g['gap_samples']+=int(gn>0)
  rootids=[i for i,(u,v) in enumerate(edges) if u==0 or v==0]
  def root_cost(bb):
   vv=[bb[i] for i in rootids]
   return 71 if len(set(vv))>1 else 35*int(vv[0]!=anchors[0])
  rg=root_cost(labels)-root_cost(bits)
  g['root_gap_numerator']+=rg;g['root_gap_positive']+=int(rg>0);g['root_gap_negative']+=int(rg<0)
  unresolved+=out['unresolved_paths'];unknown+=out['unknown_guards'];switches+=out['switches']
  samples.append({'pattern':key,'gap_numerator':gn,'rule_numerator':int(cost*71),'dp_numerator':int(best*71),'unresolved_paths':out['unresolved_paths'],'switches':out['switches']})
 denominator=71*count*len(vertices)
 rows=[]
 for k,g in groups.items():
  rows.append({'pattern':k,**g,'probability':g['count']/count,'gap_contribution_per_vertex':g['gap_numerator']/denominator,
    'root_cost_contribution':g['root_gap_numerator']/(71*count),
    'equivalent_saving_density':g['gap_numerator']/denominator/(1-float(LAM))})
 rows.sort(key=lambda x:(-x['gap_numerator'],x['pattern']))
 per=np.array([s['gap_numerator']/(71*len(vertices)) for s in samples])
 return {'depth':depth,'count':count,'seed':seed,'lambda':str(LAM),'scored_vertices':len(vertices),'boundary_vertices':len(wave[0])-len(vertices),
 'boundary':'Free leaves unscored; incomplete observed paths use finite-window cover fallback and are never switched. This is NOT the exact full infinite-tree canonical rule.',
 'pattern_definition':'root crossing degree plus sorted (opposite-to-root flag, neighbor observed crossing degree). Group assigned entire tree gap by root pattern; descriptive association, not local cause.',
 'gap_numerator_total':sum(s['gap_numerator'] for s in samples),'gap_mean_per_vertex':float(per.mean()),'gap_se':float(per.std(ddof=1)/math.sqrt(count)) if count>1 else None,
 'equivalent_saving_density_definition':'global cost gap divided by 1-lambda; not a probability, not a count of realizable saving events',
 'unresolved_path_count':unresolved,'unknown_guard_count':unknown,'switch_count':switches,'groups':rows,'samples':samples}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--depth',type=int,default=7);p.add_argument('--count',type=int,default=10000);p.add_argument('--seed',type=int,default=20261123);p.add_argument('--out',default='wave_results.json');args=p.parse_args()
 d=wave_experiment(args.depth,args.count,args.seed)
 with open(args.out,'w') as f:json.dump(d,f,sort_keys=True,indent=2)
 print(json.dumps({k:v for k,v in d.items() if k not in ('groups','samples')},indent=2))
 print('top patterns:',json.dumps(d['groups'][:3],indent=2))
