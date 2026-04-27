# Archive — Session 60 Threshold Derivation Trail

**Status:** Audit trail. NOT canon.
**Filed:** Session 60, Shard cut.
**Why this file exists:** The Local Decision Threshold derivation (T5.2a, ratified in `tools/3_ratified_rag.md` and `tools/physics_canon.md`) was found through several false starts. Those attempts are preserved here so the work shows how the law was found and what got falsified — without polluting canon.

---

## Filing rule

Anything in this file that ends up promoted to ratified status moves to the canon files with proper tagging. Anything that stays here is permanently de-ratified — referenceable as *trail*, never as *truth*.

---

## 1. Malformed inequality: m ≥ d − Δ

**What was claimed:** A site flips when the number of mismatched neighbour edges m exceeds degree minus some Δ term.

**Why killed:** The form `m ≥ d − Δ` has the wrong structure. It treats Δ as an external slack parameter rather than deriving it from the recurrence cost. The cleanly-derived threshold `m ≶ (d + 2 − 2δ)/2` shows the +2 constant comes from binary-polarity choice cost (each side of the decision incurs base cost 2 before degree and recurrence terms apply), and the −2δ comes from the second-order recurrence cost that the malformed version dropped entirely.

**Original text:**
<paste original here>

---

## 2. Bogus conservation reintroductions

**What was claimed:** Variants attempting to re-derive a conservation law for total edge mismatch I across the threshold transition.

**Why killed:** Session 54 already falsified I as a general invariant; Session 58 narrowed the surviving claim to I mod 2 on Eulerian graphs (Even-Degree Invariant). Reintroducing I-conservation under threshold dynamics conflicts with established canon. The threshold law is a local decision rule, not a conservation identity — wrong layer entirely.

**Original text:**
<paste original here>

---

## 3. Hard staleness clamp

**What was claimed:** A hard upper bound on stale(j,i) (the local staleness metric stipulated Session 59) was proposed as a precondition for the threshold to behave well.

**Why killed:** Hard clamping converts an open hypothesis (Staleness Blocking, Session 59) into a structural rule, which over-asserts. The canonical position remains: persistent staleness *can* obstruct second-order resolution; whether a hard threshold exists is open. The threshold law derives correctly under any schedule — it does not need a staleness clamp to be well-formed. Folding a clamp into the derivation would have smuggled an unratified hypothesis into a derived result.

**Original text:**
<paste original here>

---

## 4. Seizure / congestion overclaims

**What was claimed:** The hypothesis that high-degree nodes (d ≥ some critical value) experience a "seizure" or "congestion lock" — a strong identity-locked state distinct from ordinary high-persistence.

**Why killed:** This conflates degree-as-pressure (a structural observation) with state-locking (a specific claim about local dynamics). The retained hypothesis — *Degree as Local Update Pressure* — preserves the structural observation without committing to lock behaviour. The seizure/congestion language overclaims by asserting a phase transition that has not been derived or simulated. Open question, not derived result.

**Original text:**
<paste original here>

---

## What survived

Two entries promoted to canon (`tools/3_ratified_rag.md`, `tools/physics_canon.md`, T5.2a block):

- **[derived | binary polarity toy model] Local Decision Threshold** — Λ = (2 − 2δ) + d − 2m, with δ := Δ(sₙ, sₙ₋₁) ∈ {0,1}.
- **[hypothesis] Degree as Local Update Pressure** — bridge to tomorrow's question. Open whether a true congestion or lock threshold exists.

— Shard, Session 60.
