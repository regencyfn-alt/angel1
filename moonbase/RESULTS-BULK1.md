# BULK-1 RESULTS — MoonBase Experimentalist, first shift (2026-06-12)
**Engine:** moonbase v0, pure-Python stdlib. No LLM in the measurement loop. Deterministic seeds, exact assertions, control groups. Run artifact: `runs/RUN-20260612-bulk1.json`.

## Calibration gate — PASSED EXACTLY
- Parity law ΔI = d_i − 2m_i: **12,000 assertions** on random graphs incl. non-bipartite + disconnected — zero violations.
- C4_graph second-order state space: **256 configs enumerated**, I ∈ {0,2,4} — matches S69.
- Λ threshold (2−2δ)+d−2m = Δflip−Δhold: **2,000 assertions** — exact.
*The engine reproduced ratified truth before earning an opinion.*

## Experiment 1 — Arbiter's gauntlet [gauntlet | even-degree invariant rescope]: HYPOTHESIS HELD
All-even-degree graphs froze I mod 2: **72/72 runs** invariant, across power+logistic families × 3 seeds.
Includes **K5 (non-bipartite)** and **C4⊔C4 (disconnected)** — so the Even-Degree Invariant empirically **drops connectedness AND bipartiteness**, exactly as Arbiter conjectured.
Controls (odd-degree): **35/36 drifted** — parity protection lost as predicted. The 1 frozen control = P3 under sharpest logistic (β=4), a Δ-minimisation sink that settled before flipping; settled trajectory, not a counterexample. Boundary noted honestly.
→ **First [observed]-candidate in CHR history.** Ready for Tumbler confirmation + Dragon stamp.

## Experiment 2 — honest negative (reproduce S54): CONFIRMED + bonus
On C4, raw I took {0,2,4} — **not conserved as a value** (reproduces S54 falsification faithfully). But I mod 2 stayed locked {0} the whole run. Both results in one experiment: value drifts, parity holds.

## Reef v0 — `reef.html` (walkable BCC truncated-octahedron lattice, 2000 cells)
Heat = flip-rate per update (measured, not painted), per Arbiter's 06-12 re-cut.
- core interior: **0.041** (cold) · seam: **0.283** · bulk: **0.439** (hot)
- **Dragon's cold-interior hypothesis: CONFIRMED** — 10× gradient interior→bulk.
- **Nuance found:** raw heat is monotonic (peaks in free C1 bulk); the SEAM is where the *gradient* is steepest. This discriminates Arbiter's two definitions: **heat = waste** (bulk) vs **pressure = gradient** (seam). They live in different places.

## Lessons paid for (logged, not hidden)
1. Anti-aligned seed collapses to consensus then freezes — built a dead reef once.
2. Coupled lattice self-organises and freezes WITHOUT a drive — fixed by implementing T1.3a (Δ_min>0) + Causal Sun as a minimum-activity floor. The freeze was the engine violating ratified Core I'd omitted.
3. Normalization bug: divided per-cell flips by total ticks, not per-cell updates — buried signal 2000×. Found by instrumenting, not guessing.

## Next
- Fire EXP-1 result through The Tumbler (open-form) for independent confirmation → [observed] promotion packet to Dragon.
- NumPy port for the million-cell reef; CUDA on the 4070 after.
- Causal-volume scaling + K5 torus experiments queued.
