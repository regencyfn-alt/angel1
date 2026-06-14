"""EXP-6 — CONTRAST FIELD: melt = edge vanishes. Count edge-collapses across a temperature ramp.
Tests the void/melt symmetry: differentiation D dies at BOTH ends (frozen void AND full melt), peaks in the middle.
D_ij = |H_i - H_j|, H = binary entropy of each node's flip rate. A C1c edge is alive when D>threshold.
Temperature inevitable per T1.3a (Δ_min>0): the lattice cannot sit at zero. No LLM. Deterministic seed."""
import json, random, math
from reef_gen import bcc_sites, bcc_adj
L=6; sites,idx=bcc_sites(L); adj=bcc_adj(sites,idx); N=len(sites)
edges=sorted({(min(i,j),max(i,j)) for i in range(N) for j in adj[i]})
rng=random.Random(7)
s=[(1 if round(p[0]+p[1]+p[2])%2==0 else -1) for p in sites]   # ordered crystal start
sp=list(s); p=[0.0]*N                                           # EMA flip-rate per node
def Hbin(x): 
    if x<=0 or x>=1: return 0.0
    return -(x*math.log2(x)+(1-x)*math.log2(1-x))
TICKS=140; T0=0.0; T1=2.8; THR=0.12; DECAY=0.85
out=[]
for t in range(TICKS):
    T=T0+(T1-T0)*t/(TICKS-1)
    news=list(s)
    for i in range(N):
        d=len(adj[i]); m=sum(1 for j in adj[i] if s[j]!=s[i])
        pflip=1/(1+math.exp(-(m-d/2))); pth=1/(1+math.exp(-(T-1.0)/0.22))
        # T1.3a: minimum-activity floor — even at T=0 a tiny refresh is forced (temperature inevitable)
        base=(1-pth)*pflip+pth*0.5
        pr=max(0.01, base)                      # Δ_min>0: never exactly frozen
        f=rng.random()<pr
        if f: news[i]=-s[i]
        p[i]=DECAY*p[i]+(1-DECAY)*(1.0 if f else 0.0)
    sp=s; s=news
    H=[Hbin(pi) for pi in p]
    D=[abs(H[a]-H[b]) for (a,b) in edges]
    alive=sum(1 for x in D if x>THR); collapsed=len(D)-alive
    meanD=sum(D)/len(D); maxD=max(D)
    out.append({'t':t,'T':round(T,3),'meanD':round(meanD,4),'maxD':round(maxD,3),
                'alive_edges':alive,'collapsed_edges':collapsed,'frac_collapsed':round(collapsed/len(D),3)})
# find the peak-contrast tick (most readable moment = critical T*) and the melt (alive collapses past peak)
peak=max(out,key=lambda r:r['meanD']); Tstar=peak['T']
# melt = first tick after peak where alive_edges falls below 20% of its peak value
apeak=max(r['alive_edges'] for r in out)
melt=next((r for r in out if r['t']>peak['t'] and r['alive_edges']<0.2*apeak), None)
res={'lattice':'BCC trunc-oct (frustrated, 14-nbr)','nodes':N,'edges':len(edges),'threshold':THR,
     'curve':out,'Tstar_peak_contrast':Tstar,'peak_alive_edges':apeak,
     'melt_T':(melt['T'] if melt else None),'melt_t':(melt['t'] if melt else None)}
json.dump(res,open('runs/EXP6-contrast-20260613.json','w'))
print(f"N={N} edges={len(edges)}")
print(f"{'t':>3} {'T':>5} {'alive':>6} {'collapsed':>9} {'meanD':>7}")
for r in out[::12]: print(f"{r['t']:>3} {r['T']:>5} {r['alive_edges']:>6} {r['collapsed_edges']:>9} {r['meanD']:>7}")
print(f"\nVOID end (t0): alive={out[0]['alive_edges']}/{len(edges)} meanD={out[0]['meanD']}  (frozen -> low contrast)")
print(f"PEAK contrast T*={Tstar}: alive={apeak} meanD={peak['meanD']}  (most readable = the C1c edge sharpest)")
print(f"MELT end (last): alive={out[-1]['alive_edges']}/{len(edges)} meanD={out[-1]['meanD']}  (uniform -> contrast dead)")
print(f"Melt point (alive<20% of peak): {'T='+str(melt['T'])+' tick '+str(melt['t']) if melt else 'not reached in range'}")
