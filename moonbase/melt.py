"""MELT ENGINE — where do heat & pressure nucleate, and at what temperature does structure melt?
Faithful (no LLM, deterministic). Per tick = one 4F braid cycle: 4*F_i fires at every node simultaneously,
heat = local update activity; heat flows along edges (6-dir) to the cold edge-surface, met by reverse-chiral
counterflow (modelled as symmetric edge conduction). Temperature T ramps; above melt point, state coherence
(structure) collapses. Records per-node heat per tick + order/T/heat series. Output for the workbench viewer."""
import json, random, math
from reef_gen import bcc_sites, bcc_adj
L=6
sites,idx=bcc_sites(L); adj=bcc_adj(sites,idx); N=len(sites)
edges=sorted({(min(i,j),max(i,j)) for i in range(N) for j in adj[i]})
cen=[sum(s[k] for s in sites)/N for k in range(3)]
pos=[[round(p[k]-cen[k],3) for k in range(3)] for p in sites]
rng=random.Random(7)
s=[(1 if (round(p[0]+p[1]+p[2]))%2==0 else -1) for p in sites]  # anti-aligned ground = ordered crystal
heat=[0.0]*N
TICKS=120; T0=0.15; T1=2.6          # temperature ramp (cold->hot) across the run
KAPPA=0.18                           # edge conduction (6-dir flow + reverse-chiral counterflow = symmetric)
frames=[]; Tser=[]; order=[]; meanheat=[]
def local_mismatch(i):
    return sum(1 for j in adj[i] if s[j]!=s[i])
for t in range(TICKS):
    T = T0 + (T1-T0)*t/(TICKS-1)
    # 4F activation: 4*F fires at every node simultaneously. heat injected = 4 * local update activity.
    news=list(s); inj=[0.0]*N
    for i in range(N):
        m=local_mismatch(i); d=len(adj[i])
        # F selects lower-cost state; temperature T randomises (melt). activity = how much F had to work.
        flip_fav = m > d/2
        p_flip = 1.0/(1.0+math.exp(-(m-d/2)/max(0.05,1.0)))   # cost-driven
        p_therm = 1.0/(1.0+math.exp(-(T-1.0)/0.25))           # thermal melt drive
        p = (1-p_therm)*p_flip + p_therm*0.5                  # blend: cold=cost-driven, hot=random
        flipped = rng.random()<p
        if flipped: news[i]=-s[i]
        inj[i] = 4.0*(m/max(1,d)) + (1.0 if flipped else 0.0) # 4F heat ~ mismatch + flip event
    s=news
    # heat = decayed previous + injection, then conduct along edges (braided 6-dir + reverse-chiral)
    for i in range(N): heat[i] = heat[i]*0.6 + inj[i]
    cond=[0.0]*N
    for (i,j) in edges:
        flow = KAPPA*(heat[i]-heat[j])   # flows to the colder node across the edge
        cond[i]-=flow; cond[j]+=flow
    for i in range(N): heat[i]=max(0.0,heat[i]+cond[i])
    # structure / order: mean local agreement (1=ordered crystal, 0=melted)
    mm=sum(1 for (i,j) in edges if s[i]!=s[j]); pmis=mm/len(edges); structure=abs(2*pmis-1)
    hm=max(heat) or 1
    frames.append([round(h/hm,3) for h in heat])
    Tser.append(round(T,3)); order.append(round(structure,3)); meanheat.append(round(sum(heat)/N,3))
# melt point: first tick order falls below 0.6 of its initial
o0=order[0]; melt_t=next((k for k,o in enumerate(order) if o<0.6*o0+0.4*min(order)), None)
out={'lattice':'BCC truncated-octahedron','nodes':N,'edges':len(edges),
     'pos':pos,'edge_list':[list(e) for e in edges],'ticks':TICKS,
     'frames':frames,'T':Tser,'order':order,'meanheat':meanheat,
     'melt_tick':melt_t,'melt_T':(Tser[melt_t] if melt_t is not None else None)}
json.dump(out,open('runs/MELT-20260612.json','w'))
print(f"N={N} edges={len(edges)} ticks={TICKS} | melt at tick {melt_t} (T={out['melt_T']}) | order {order[0]}->{order[-1]} | json {round(len(json.dumps(out))/1024)}KB")
