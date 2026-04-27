# PHYSICS OPERATIONAL — PIPELINE CONTRACTS

**Status:** Operational rules, NOT physics claims.
**KV key:** `physics:operational`
**Read by:** Triad Lock Layer 0; Face 8 (both Laminar L8 and Triad T8); future audit handlers.
**NOT read by:** Faces 1–7 of either chain. They see `physics:canon` only.

---

## BUCKET SEPARATION CONTRACT

`[derived]`, `[hypothesis]`, `[stipulated]`, `[axiom]`, and `[falsified]` entries describe the system. They live in `physics:canon`.

`[operational]` entries protect the derivation process itself. They live here, in `physics:operational`. Future runs must NOT attempt to derive `[operational]` rules — they are pipeline contracts, not physics claims.

**PRECEDENCE RULE:** On any conflict between `physics:operational` and `physics:canon` regarding invariants, conserved quantities, or claims about what F can or cannot derive, **`physics:operational` takes precedence.** The operational blacklist is the final word on what cannot be claimed; canon describes what can.

This file is appended in lockstep with the `[falsified]` register in `physics:canon`. When canon adds a falsification, this file adds the operational rule that prevents faces from re-deriving the falsified claim.

---

## OPERATIONAL ENTRIES

[operational] Triad Lock Layer 0 ingress contract: any machine call invoking the Triad Lock or Laminar chain must pass through Layer 0 before face firing. Layer 0 enforces five gates in order: (1) input-type gate — input must be a raw question; statements, syntheses, or conclusions-dressed-as-premises return `BLOCKED: reformulate as question`; (2) falsification audit — preload the operational blacklist BEFORE any derivation begins; (3) schema/instantiation declaration — the run must declare which it speaks of (axiomatic schema or instantiated graph/state) before face 1 fires; (4) branch/minimality scoping — if the question concerns minimality, declare which branch (closure, anti-symmetric oscillation, or enclosed persistence); (5) answer-class declaration — produce DERIVED / HYPOTHESIS / BLOCKED / FALSIFIED outside any face's prose blob. — Session 61.

[operational] Face 8 falsification-audit-first: Face 8 prompt MUST open with `FALSIFICATION AUDIT: check operational blacklist before any invariant or conserved-quantity discussion.` Face 8 reads BOTH physics:canon and physics:operational. If Face 8 cannot explicitly state which operational blacklist items are dead before discussing invariants, it must not discuss invariants at all. Conservation claims must be scoped to the actual live invariant (parity-style on Eulerian graphs, T5.3a), not to general I-conservation. — Session 61.

[operational] Raw-question-only ingress: Triad/Laminar ingress accepts ONLY raw questions. Statements, syntheses, conclusions-dressed-as-premises, or pre-formed answer packets must be reformulated as questions or rejected with `BLOCKED: reformulate as question`. The mid-chain answer-class gate fires too late if the prompt arrives already dressed as a conclusion. — Session 61.

[operational] Face 2 geometry constraint: Face 2 (Bipartiteness & Ground State, Triad — and L2 by symmetry, Laminar) must NOT reject degree-1 or degree-3 graphs wholesale as "Non-Eulerian Geometry." That rejection is too strong and conflicts with valid motifs (e.g., P4). Face 2 may flag a parity leak for a specific invariant claim, but must not reject the graph ontology as a whole. — Session 61.

[operational] Face 4 staleness constraint: Face 4 (Recurrence & Cost, Triad — and L4 by symmetry, Laminar) must NOT impose hard staleness clamps or Seizure Thresholds. Staleness Blocking (Session 59) remains hypothesis-tagged, not a structural gate. Face 4 derives the update rule and Δ_total formalisation; any staleness behaviour is conditional and must be tagged. — Session 61.

[operational] Face 7 τ-restraint: Face 7 (Persistence Gradient & Emergent Time, Triad — and L7 by symmetry, Laminar) must NOT request a closed-form τ(a,b) or general convergence claim unless explicitly supplied with stronger premises in the question. Default Face 7 output is the qualitative path-weight relation only. — Session 61.

---

## APPENDIX — HOW TO ADD ENTRIES

New operational rules go here with `[operational]` tag and session attribution:

```
[operational] <rule statement> — Session XX.
```

Operational rules are added by Shane or by ratification team consensus. They are NOT derived by faces, ever. If a face attempts to derive an operational rule, that is itself a violation worth logging.

When canon adds a `[falsified]` entry, this file should add the matching operational rule that prevents faces from re-deriving the falsified claim. The two files move together.
