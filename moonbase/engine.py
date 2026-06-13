#!/usr/bin/env python3
"""MoonBase Engine v0 — CHR binary-polarity substrate. Pure stdlib. Minimal excellence:
no LLM in the measurement loop; deterministic seeds; exact assertions; control groups.
Canon: T0.1-T0.6, S58 Parity (rescoped 2026-06-12), S60 Lambda, S69 C4 state space, Rung 3 family."""
import json, random, itertools, sys, time

# ---------- graphs (adjacency lists) ----------
def cycle(n, off=0): return {off+i: [off+(i-1)%n, off+(i+1)%n] for i in range(n)}
def complete(n, off=0): return {off+i: [off+j for j in range(n) if j!=i] for i in range(n)}
def disjoint(*gs):
    g={} ;  [g.update(x) for x in gs]; return g
def path(n, off=0): return {off+i: [x+off for x in ([i-1] if i>0 else [])+([i+1] if i<n-1 else [])] for i in range(n)}
def star(k, off=0):
    g={off:[off+1+i for i in range(k)]}
    for i in range(k): g[off+1+i]=[off]
    return g
def circulant(n, jumps, off=0):
    g={off+i:[] for i in range(n)}
    for i in range(n):
        for s in jumps:
            for j in ((i+s)%n,(i-s)%n):
                if off+j not in g[off+i] and j!=i: g[off+i].append(off+j)
    return g
def random_simple(n, p, rng):
    g={i:[] for i in range(n)}
    for i in range(n):
        for j in range(i+1,n):
            if rng.random()<p: g[i].append(j); g[j].append(i)
    return g
def edges_of(g):
    return [(u,v) for u in g for v in g[u] if u<v]
def degrees(g): return {u:len(g[u]) for u in g}
def all_even(g): return all(d%2==0 for d in degrees(g).values())

# ---------- state & measures ----------
def mismatch_I(g, s):
    return sum(1 for u,v in edges_of(g) if s[u]!=s[v])
def m_i(g, s, i):  # mismatched incident edges at i (canon referent lock)
    return sum(1 for j in g[i] if s[j]!=s[i])

# ---------- update families (Rung 3) ----------
def delta_total(g, s, sp, i, c):
    d = (0 if c==s[i] else 1) + (0 if c==sp[i] else 1)
    d += sum(0 if c==s[j] else 1 for j in g[i])
    return d
def step(g, s, sp, i, rng, fam, par):
    cands=(1,-1)
    if fam=='power':  w=[ (1+delta_total(g,s,sp,i,c))**(-par) for c in cands]
    else:             w=[ pow(2.718281828, -par*delta_total(g,s,sp,i,c)) for c in cands]
    tot=w[0]+w[1]; r=rng.random()*tot
    c = cands[0] if r<w[0] else cands[1]
    sp[i]=s[i]; s[i]=c
    return c

# ---------- calibration gate ----------
def calibrate(rng):
    rep={}
    # T1 Parity law: ANY finite simple graph (incl non-bipartite, disconnected), forced flips
    trials=0
    for t in range(300):
        n=rng.randint(2,14); g=random_simple(n, rng.uniform(0.1,0.9), rng)
        s={i:rng.choice((1,-1)) for i in g}
        for _ in range(40):
            i=rng.randrange(n); I0=mismatch_I(g,s); d=len(g[i]); m=m_i(g,s,i)
            s[i]=-s[i]; I1=mismatch_I(g,s)
            assert I1-I0 == d-2*m, f"PARITY VIOLATION graph={g} site={i}"
            assert (I1-I0)%2 == d%2
            trials+=1
    rep['T1_parity_assertions']=trials
    # T2 C4 second-order state space: 4 sites x (s,sp) -> 4^4=256; I in {0,2,4}
    g=cycle(4); states=[(1,1),(1,-1),(-1,1),(-1,-1)]; Ivals=set(); count=0
    for cfg in itertools.product(states, repeat=4):
        s={i:cfg[i][0] for i in range(4)}; Ivals.add(mismatch_I(g,s)); count+=1
    assert count==256 and Ivals=={0,2,4}, (count,Ivals)
    rep['T2_C4_configs']=count; rep['T2_I_values']=sorted(Ivals)
    # T3 Lambda threshold: L=(2-2*delta)+d-2m == Dflip-Dhold
    for t in range(2000):
        n=rng.randint(2,12); g=random_simple(n,0.5,rng)
        s={i:rng.choice((1,-1)) for i in g}; sp={i:rng.choice((1,-1)) for i in g}
        i=rng.randrange(n); d=len(g[i]); m=m_i(g,s,i); dl=0 if s[i]==sp[i] else 1
        Dh=delta_total(g,s,sp,i,s[i]); Df=delta_total(g,s,sp,i,-s[i])
        assert Df-Dh == (2-2*dl)+d-2*m
    rep['T3_lambda_assertions']=2000
    return rep

# ---------- Experiment 1: EDI gauntlet ----------
def edi_run(name, g, fam, par, seed, T=20000):
    rng=random.Random(seed); nodes=list(g)
    s={i:rng.choice((1,-1)) for i in nodes}; sp={i:rng.choice((1,-1)) for i in nodes}
    p0=mismatch_I(g,s)%2; flips_par=0
    for t in range(T):
        i=nodes[rng.randrange(len(nodes))]
        step(g,s,sp,i,rng,fam,par)
        if mismatch_I(g,s)%2 != p0: flips_par+=1; p0=mismatch_I(g,s)%2
    return flips_par
def experiment1():
    out=[]
    graphs = {
      'C4 (even,bipartite,connected)': cycle(4),
      'C6 (even,bipartite,connected)': cycle(6),
      'K5 (even4,NON-bipartite,connected)': complete(5),
      'C4+C4 (even,DISCONNECTED)': disjoint(cycle(4), cycle(4,10)),
      'Circulant C8(1,3) (even4)': circulant(8,(1,3)),
      'Circulant C10(2,3) (even4,non-bip)': circulant(10,(2,3)),
      'CTRL P3 (odd ends)': path(3),
      'CTRL K4 (3-regular odd)': complete(4),
      'CTRL Star3 (odd)': star(3),
    }
    for name,g in graphs.items():
        ev=all_even(g)
        for fam,par in (('power',1),('power',4),('logistic',1),('logistic',4)):
            for seed in (11,23,47):
                pc=edi_run(name,g,fam,par,seed)
                out.append({'graph':name,'all_even':ev,'family':fam,'param':par,'seed':seed,
                            'parity_changes':pc,'ticks':20000})
    return out

# ---------- Experiment 2: honest negative (S54) ----------
def experiment2():
    g=cycle(4); rng=random.Random(99); nodes=list(g)
    s={i:rng.choice((1,-1)) for i in nodes}; sp={i:rng.choice((1,-1)) for i in nodes}
    seen=set()
    for t in range(5000):
        step(g,s,sp,nodes[rng.randrange(4)],rng,'power',2); seen.add(mismatch_I(g,s))
    return {'graph':'C4','ticks':5000,'distinct_I_values_observed':sorted(seen),
            'I_conserved_as_value': len(seen)==1, 'I_mod2_values':sorted({x%2 for x in seen})}

if __name__=='__main__':
    t0=time.time(); rng=random.Random(7)
    cal=calibrate(rng); print('CALIBRATION GATE PASSED:', json.dumps(cal))
    e1=experiment1(); e2=experiment2()
    res={'run':'BULK-1','date':'2026-06-12','engine':'moonbase v0 (pure python, stdlib)',
         'calibration':cal,'experiment1_EDI_gauntlet':e1,'experiment2_S54_negative':e2,
         'seconds':round(time.time()-t0,1)}
    with open('runs/RUN-20260612-bulk1.json','w') as f: json.dump(res,f,indent=1)
    even_ok=[r for r in e1 if r['all_even'] and r['parity_changes']==0]
    even_bad=[r for r in e1 if r['all_even'] and r['parity_changes']>0]
    ctrl_drift=[r for r in e1 if not r['all_even'] and r['parity_changes']>0]
    ctrl_frozen=[r for r in e1 if not r['all_even'] and r['parity_changes']==0]
    print(f"EXP1: even-degree runs invariant: {len(even_ok)}/{len(even_ok)+len(even_bad)} | controls drifting: {len(ctrl_drift)}/{len(ctrl_drift)+len(ctrl_frozen)}")
    print('EXP2:', json.dumps(e2))
    print('seconds:', res['seconds'])
