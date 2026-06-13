"""Reef snapshot generator. Builds a BCC lattice (14-neighbour truncated-octahedron packing),
embeds a persistent C3 core in C1 bulk, runs the real engine, measures per-cell HEAT =
update-path waste (flip-rate over a window). Tests Dragon's 06-12 hypothesis visually:
C3 interior cold, seams hot. No LLM, pure measurement."""
import json, random, math
def bcc_sites(L):
    sites=[]; idx={}
    for x in range(L):
        for y in range(L):
            for z in range(L):
                for off in (0.0,0.5):
                    p=(x+off,y+off,z+off)
                    if all(c<L for c in p): idx[p]=len(sites); sites.append(p)
    return sites, idx
def bcc_adj(sites, idx):
    adj=[[] for _ in sites]; S=set(idx)
    dirs=[(dx,dy,dz) for dx in(-.5,.5) for dy in(-.5,.5) for dz in(-.5,.5)]+\
         [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    for p,i in idx.items():
        for d in dirs:
            q=(round(p[0]+d[0],1),round(p[1]+d[1],1),round(p[2]+d[2],1))
            if q in idx: adj[i].append(idx[q])
    return adj
L=10
sites,idx=bcc_sites(L); adj=bcc_adj(sites,idx); N=len(sites)
cx=cy=cz=L/2; core_h=3.0  # cubic crystal half-width (Chebyshev)
def in_core(p): return max(abs(p[0]-cx),abs(p[1]-cy),abs(p[2]-cz))<=core_h  # cube
core=[in_core(p) for p in sites]
rng=random.Random(2026)
s=[rng.choice((1,-1)) for _ in sites]  # random init (no collapse bias)
sp=list(s)
# per-cell alpha: core persistent (high), bulk churny (low)
alpha=[9.0 if core[i] else 0.12 for i in range(N)]  # crystal locks hard (C3), bulk churns (C1)
def dtot(i,c):
    d=(0 if c==s[i] else 1)+(0 if c==sp[i] else 1)
    return d+sum(0 if c==s[j] else 1 for j in adj[i])
WARM=200000; MEAS=600000; flips=[0]*N; upd=[0]*N
for t in range(WARM+MEAS):
    i=rng.randrange(N); a=alpha[i]
    w1=math.exp(-a*dtot(i,1)); w2=math.exp(-a*dtot(i,-1))
    c=1 if rng.random()*(w1+w2)<w1 else -1
    if rng.random()<0.04: c=rng.choice((1,-1))  # T1.3a Δ_min>0 + Causal Sun: minimum-activity drive
    if t>=WARM:
        upd[i]+=1
        if c!=s[i]: flips[i]+=1
    sp[i]=s[i]; s[i]=c
heat=[ (flips[i]/upd[i] if upd[i] else 0.0) for i in range(N)]  # flip-rate per update = update-path waste
hmax=max(heat) or 1
# classify seam = core cell adjacent to bulk, or bulk cell adjacent to core
seam=[ (core[i]!=core[j] for j in adj[i]) for i in range(N)]
seam=[any(any(core[i]!=core[j] for j in adj[i]) for _ in [0]) for i in range(N)]
core_heat=[heat[i] for i in range(N) if core[i] and not seam[i]]
seam_heat=[heat[i] for i in range(N) if seam[i]]
bulk_heat=[heat[i] for i in range(N) if not core[i] and not seam[i]]
def avg(x): return round(sum(x)/len(x),4) if x else None
report={'lattice':'BCC truncated-octahedron','cells':N,'core_halfwidth':core_h,
        'core_interior_mean_heat':avg(core_heat),'seam_mean_heat':avg(seam_heat),
        'bulk_mean_heat':avg(bulk_heat),
        'PREDICTION_cold_interior_hot_seam': (avg(core_heat) is not None and avg(seam_heat) is not None and avg(core_heat) < avg(seam_heat))}
cells=[{'p':[round(c,2) for c in sites[i]],'h':round(heat[i]/hmax,3),
        'core':core[i],'seam':seam[i]} for i in range(N)]
json.dump({'report':report,'hmax':round(hmax,4),'cells':cells},
          open('runs/REEF-20260612.json','w'))
print(json.dumps(report,indent=1))
