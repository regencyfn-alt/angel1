import json, random
from engine import path, complete, star, edi_run, all_even, degrees
graphs={'P3':path(3),'K4':complete(4),'Star3':star(3)}
print("Chasing the frozen control — per-run parity_changes:")
for name,g in graphs.items():
    for fam,par in (('power',1),('power',4),('logistic',1),('logistic',4)):
        for seed in (11,23,47):
            pc=edi_run(name,g,fam,par,seed)
            tag = "  <-- FROZEN" if pc==0 else ""
            if pc==0: print(f"  {name:6} deg={list(degrees(g).values())} {fam}/{par} seed={seed}: {pc}{tag}")
