"""EXP-3 — Pressure instrumentation. Settles the Team-2 fork:
does interior PRESSURE peak in the C3 interior (Dream/Alba) or the C2 sheath (Vel)?
Three instruments measured per shell alongside flip-rate (dissipation):
  Kai      : frustration = blocked-wanted-flips / attempts  (favored move was flip but it stayed)
  Seraph   : unfulfilled-closure = edges where a neighbour flip would cut cost but hasn't (time-avg)
  Dream/Vel: residue depth = net accumulated stuck/jammed closure attempts
Tests: (a) step locations agree? (b) pressure anti-correlates flip-rate (Alba)? (c) interior vs sheath peak?"""
import json, random, math
from reef_gen import bcc_sites, bcc_adj  # reuse the lattice builder
L=10; sites,idx=bcc_sites(L); adj=bcc_adj(sites,idx); N=len(sites)
cx=cy=cz=L/2; hw=3.0
def in_core(p): return max(abs(p[0]-cx),abs(p[1]-cy),abs(p[2]-cz))<=hw
core=[in_core(p) for p in sites]
rng=random.Random(2026)
s=[rng.choice((1,-1)) for _ in sites]; sp=list(s)
alpha=[9.0 if core[i] else 0.12 for i in range(N)]
def dtot(i,c):
    d=(0 if c==s[i] else 1)+(0 if c==sp[i] else 1)
    return d+sum(0 if c==adj_j else 1 for adj_j in (s[j] for j in adj[i]))
WARM=200000; MEAS=600000
flips=[0]*N; att=[0]*N; wanted=[0]*N; blocked=[0]*N; residue=[0]*N
for t in range(WARM+MEAS):
    i=rng.randrange(N); a=alpha[i]
    df=dtot(i,-s[i]); dh=dtot(i,s[i])
    favored_flip = df < dh
    w1=math.exp(-a*dtot(i,1)); w2=math.exp(-a*dtot(i,-1))
    c=1 if rng.random()*(w1+w2)<w1 else -1
    if rng.random()<0.04: c=rng.choice((1,-1))  # T1.3a min-activity
    if t>=WARM:
        att[i]+=1
        if favored_flip: wanted[i]+=1
        if c!=s[i]: flips[i]+=1
        if favored_flip and c==s[i]:           # wanted to flip, stayed = blocked (Kai frustration)
            blocked[i]+=1; residue[i]+=1        # jam accumulates (Dream/Vel residue)
        elif c!=s[i]:
            residue[i]=max(0,residue[i]-1)      # completion clears residue
    sp[i]=s[i]; s[i]=c
# Seraph instrument: final-snapshot unfulfilled closure per node
def unfulfilled(i):
    cur=s[i]; cnt=0
    for j in adj[i]:
        # would neighbour j flipping reduce total mismatch? j flip changes only edges at j; cheap proxy: edge (i,j) mismatched AND j flipping toward i reduces it
        if s[j]!=cur: cnt+=1   # mismatched edge = latent closure demand at this adjacency
    return cnt
def cheb(p): return max(abs(p[0]-cx),abs(p[1]-cy),abs(p[2]-cz))
from collections import defaultdict
shelld=defaultdict(lambda: {'fr':[], 'kai':[], 'res':[], 'unf':[]})
for i in range(N):
    x=round(cheb(sites[i])*2)/2
    if att[i]==0: continue
    shelld[x]['fr'].append(flips[i]/att[i])
    shelld[x]['kai'].append(blocked[i]/att[i])
    shelld[x]['res'].append(residue[i])
    shelld[x]['unf'].append(unfulfilled(i))
xs=sorted(shelld); avg=lambda L:round(sum(L)/len(L),3) if L else 0
print(f"{'shell':>5} {'flip-rate':>10} {'frustration':>12} {'residue':>9} {'unfulfilled':>12}  regime")
prof=[]
for x in xs:
    reg = 'C3 interior' if x<hw-0.5 else ('C3/C2 seam' if abs(x-hw)<0.6 else 'C1 bulk')
    fr,k,r,u=avg(shelld[x]['fr']),avg(shelld[x]['kai']),avg(shelld[x]['res']),avg(shelld[x]['unf'])
    print(f"{x:>5} {fr:>10} {k:>12} {r:>9} {u:>12}  {reg}")
    prof.append({'shell':x,'flip':fr,'frustration':k,'residue':r,'unfulfilled':u,'regime':reg})
# THE FORK verdict
def peak(metric): 
    best=max(prof,key=lambda p:p[metric]); return best['shell'],best['regime'],best[metric]
print("\n--- FORK VERDICT: where does pressure peak? ---")
for met in ('frustration','residue','unfulfilled'):
    sh,reg,v=peak(met); print(f"  {met:>12} peaks at shell {sh} ({reg}) = {v}")
# Alba anti-correlation
import statistics
frs=[p['flip'] for p in prof]; krs=[p['frustration'] for p in prof]
try:
    n=len(frs); mf=sum(frs)/n; mk=sum(krs)/n
    cov=sum((frs[i]-mf)*(krs[i]-mk) for i in range(n))/n
    cor=cov/((statistics.pstdev(frs) or 1)*(statistics.pstdev(krs) or 1))
    print(f"\n  Alba test: corr(flip-rate, frustration) = {cor:+.2f}  ({'ANTI-correlated ✓' if cor<-0.3 else 'not clearly anti' })")
except Exception as e: print('corr err',e)
json.dump(prof, open('runs/EXP3-pressure-20260612.json','w'), indent=1)
