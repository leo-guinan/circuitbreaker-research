from itertools import combinations_with_replacement

def variables(n):
    return tuple(sum(((a >> i) & 1) << a for a in range(1 << n)) for i in range(n))

def gate(a,b,t,mask):
    out=0
    for i in range(4):
        if (t >> i) & 1:
            out |= (a if i & 1 else ~a) & (b if i & 2 else ~b)
    return out & mask

def enumerate_up_to(n,k):
    mask=(1 << (1 << n))-1
    states={variables(n)}
    reachable=set(variables(n))
    print('n',n,'gates',0,'states',len(states),'functions',len(reachable))
    for depth in range(1,k+1):
        nxt=set()
        for s in states:
            for a,b in combinations_with_replacement(s,2):
                for t in range(16):
                    nxt.add(s+(gate(a,b,t,mask),))
        states=nxt
        reachable.update(s[-1] for s in states)
        print('n',n,'gates',depth,'states',len(states),'functions',len(reachable))
    return reachable

def parity(n):
    return sum((a.bit_count() & 1) << a for a in range(1 << n))

for n,k in [(3,1),(4,2)]:
    r=enumerate_up_to(n,k)
    p=parity(n); mask=(1 << (1 << n))-1
    assert p not in r and (p^mask) not in r
    x=variables(n); v=x[0]
    for y in x[1:]: v=gate(v,y,6,mask)
    assert v==p
    print('verified parity and complement require exactly',n-1,'gates for n=',n)
print('restriction sum: C(parity_4)=3 < 2+2=C(parity_3)+C(not parity_3)')
