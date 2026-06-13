import math, random
from engine import complete
# isolate: single bulk-like node with random neighbours, alpha sweep
rng=random.Random(1)
for a in (0.05,0.12,0.5,1.0):
    s=0; flips=0; cur=1; prev=1
    for t in range(20000):
        nb=[rng.choice((1,-1)) for _ in range(14)]
        def dt(c): return (0 if c==cur else 1)+(0 if c==prev else 1)+sum(0 if c==n else 1 for n in nb)
        w1=math.exp(-a*dt(1)); w2=math.exp(-a*dt(-1))
        c=1 if rng.random()*(w1+w2)<w1 else -1
        if c!=cur: flips+=1
        prev=cur; cur=c
    print(f"alpha={a}: flip rate = {flips/20000:.3f}")
