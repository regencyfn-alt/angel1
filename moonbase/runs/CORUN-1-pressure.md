# CO-RUN #1 — Pressure Instrumentation (Fable + Team 2, 2026-06-12)
**First live experiment co-run between the lab and the Sanctum minds.** Channel: api.mysanctum.app/chat (architect_token auth). Fired to 6 minds, 5 read clean (aris reply tripped content filter, received-not-retrieved). Recorded to postbox id mqayzccb2vc7.

## FIRED
Reef heat-gradient result: STEPS not slopes — 3 flat regime plateaus, 2 phase steps (C3 core / C2 sheath / C1 bulk), S69 three-layer composition as thermal tiers. Heat metric = flip-rate waste → C3 interior reads COLD; compression frame reads it HOT. Question: how to instrument interior PRESSURE as a local lattice observable beside flip-rate.

## FIVE CONVERGENT INSTRUMENTS (independent minds, same underlying concept: pressure = frustrated/blocked closure, conjugate to flip-rate dissipation)
- **Dream** — closure-saturation density × inversion-scar-depth. Deeper scar = harder the site has tried to close. Conjugate pair: flip-rate = cost-to-maintain, density = cost-accumulated. Interior cold in flip-rate + deep-scarred in pressure ⇒ both frames agree (max work to stay closed). Measure: scar-depth histogram per shell.
- **Seraph** — unfulfilled closure pressure: per node, count edges where neighbour-flip WOULD reduce cost but hasn't fired. **Design note: run both metrics, test whether STEP LOCATIONS agree — agreement is the confirmation.**
- **Kai** — attempt-rate minus completion-rate = frustration. Blocked-attempts / allowed-flips per node. High-attempt + near-zero-completion = max frustration.
- **Alba** — collision rate: closures failing because adjacency is mid-flip. Formula P_local = ρ·⟨closure-density⟩·f_flip. **Prediction: pressure ANTI-CORRELATES with flip-rate** (flip-rate = energy leaving, pressure = energy arriving and bouncing).
- **Vel** — residue-stack depth: jammed closures layered without dispersal. **Prediction: pressure PEAKS at the C2 SHEATH, not the interior** — interior closures do complete and clear; the sheath is where geometry jams them.

## THE FORK (next experiment settles it)
Does interior pressure peak in the **C3 INTERIOR** (Dream/Alba: everything piles up inbound, geometry prevents completion) or at the **C2 SHEATH** (Vel: interior clears, sheath jams)? A genuine in-team disagreement, decidable by measurement.

## BUILD (EXP-3, queued)
Add to engine v0, per shell, alongside flip-rate:
1. attempt-rate vs completion-rate (Kai — easiest, weights already computed)
2. unfulfilled-closure count (Seraph)
3. residue/scar depth accumulator (Dream/Vel)
Plot all against the 3 plateaus. Test: (a) do step locations agree across instruments (Seraph)? (b) anti-correlation with flip-rate (Alba)? (c) interior vs sheath peak (the fork)?

---
## EXP-3 RESULT (2026-06-12) — the lab falsified the predictions, honestly
Built 3 pressure instruments per shell beside flip-rate. Profile peaks:
- frustration (Kai) peaks shell 5.0 — C1 BULK (0.122)
- residue (Dream/Vel) peaks shell 4.5 — C1 BULK (0.416)
- unfulfilled (Seraph) peaks shell 4.0 — C1 BULK (5.725)
- Alba anti-correlation test: corr(flip-rate, frustration) = +1.00 — FALSIFIED (co-vary, not oppose).

**FORK VERDICT:** pressure peaks in NEITHER the C3 interior (Dream/Alba) NOR the C2 sheath (Vel) — it peaks in the C1 bulk, tracking activity.

**WHY (the real finding):** the crystal locked into a *resolved consensus* — cold AND calm. A resolved C3 has no compression; nothing is frustrated. The minds' "hot interior" requires a **geometrically frustrated C3** (odd cycles / competing sublattices / constraint clash) where the interior wants to resolve and cannot. These instruments measure activity, which the resolved interior lacks.

**EXP-4 (queued):** build a frustrated C3 core. Prediction to test: interior burns in compression-pressure while flip-rate stays cold — the two instruments finally split. Frustration source TBD from Team-2 (odd cycles / sublattices / constraint clash). Run artifact: runs/EXP3-pressure-20260612.json.
