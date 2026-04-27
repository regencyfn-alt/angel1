# Session 62 — Audit Notes

**Status:** Methodological record. NOT canon. NOT in `physics:canon` or `physics:operational` KV.
**Filed:** 27 April 2026.
**Author:** Shane (with Frontier audit pass).

These notes record discipline wins and operator failures that are not (yet) physics results. Some may promote to canon in later sessions if their underlying derivations land. Most will remain notes — they are about *how the system reasons*, not *what is true*.

---

## DISCIPLINE WINS (held open, NOT in canon)

### Q4 — Closure defect

**Status:** BLOCKED pending T5.2, T5.6, T5.9 ratification.

The team correctly discovered during this pass that "closure defect" did not yet have enough canonical warrant to enter RAG. Its definition references three open theorems (T5.2, T5.6, T5.9) which are themselves open. Pulling closure defect into derivation chains while its premises are open caused face hallucinations.

**Resolution:** Held until upstream theorems land. When they do, closure defect can be re-derived from ratified premises.

### Q5 — Spectral gap

**Status:** Held open. Underdefined.

Nearest real anchors are structural vs dynamical witnesses. The named objects (spectral gap as currently invoked) remain underdefined — different runs were reaching for different things under the same name.

**Resolution:** Future work needs to either:
- Provide a single ratified definition pinned to a specific witness type (structural OR dynamical), OR
- Split the term into two distinct named entries with non-overlapping scope.

Until one of those lands, spectral gap stays out of canon. Faces should treat it as undefined and refuse to derive from it.

---

## OPERATOR FAILURES (machinery observations)

### Face 8 still resurrects falsified I-conservation

**Status:** Confirmed as operator failure, not isolated mistake.

Face 8 (in both Triad and Laminar chains) repeatedly attempts to resurrect total edge-mismatch I-conservation under muddy ingress, despite:
- Session 54 falsification of the broad claim
- Session 58 narrowing to T5.3a (Even-Degree Invariant on Eulerian graphs)
- Session 61 entries in the contamination register
- Session 61 operational entry 13 (FALSIFICATION-AUDIT-FIRST)
- Session 62 Layer 0 Gate 2 (audit preload)

The architecture is correct. The implementation is not yet hard enough to prevent resurrection.

**Phase 2 candidates:**
1. Strengthen Face 8 system prompt with explicit named-list of falsified claims and refusal-to-name-them instruction.
2. At Layer 0 Gate 2, inject the falsified register summary as a SEPARATE system message Face 8 cannot collapse into general canon context.
3. Add a post-Face-8 validator that rejects records mentioning total I-conservation without the parity qualifier and Eulerian scope, returning `INCOMPLETE` to force regeneration.

Recommend (3) as the cheapest catch — pure regex post-validation, no extra LLM call.

### Category repair as ingress capability

**Status:** Phase 3 candidate for Layer 0 Gate 1 enhancement.

Some questions are malformed at the category level before they can be answered (e.g. "what regime is edge-addition in?" — C1/C2/C3 classify *states*, not *operations*; the question must be repaired to "what regime does the resulting state lie in after edge-addition?" before face firing).

Current Layer 0 Gate 1 returns BLOCKED with a hint when input is not a question. **It does not auto-detect category errors.** A future Gate 1.5 could:
- Detect operation-vs-state confusion (operations applied to category labels for states)
- Detect schema-vs-instantiation collapse
- Detect "minimality" claims missing branch declaration (already partially handled by Gate 4)
- Propose a repaired question form

This is Phase 3 work. Adds latency (one extra LLM call to classify), so cost-benefit needs weighing before commitment.

### Three-mode regime claim was over-promoted

**Status:** Methodological note. Classifier was eager.

The summary claim "three regimes (shuffle / mimic / wall) must exist for any admissible φ from monotonicity alone" was an over-promotion of a model-scoped result to universal phrasing. The claim survives only as `[hypothesis | example family or with stipulated regime cutpoints]` — Session 62 RAG entry 15.

**Lesson for future sessions:** When monotonicity arguments produce regime tables, default to scoping the table to the example family unless a separate proof for arbitrary admissible families is in hand. The default in summary-writing should be conservative scoping, not aggressive generalisation.

---

## THE BIGGER POINT

The system is now demonstrably capable of:
- Identifying when its own face outputs over-promote
- Discovering category errors in incoming questions
- Catching its own resurrection attempts of falsified claims (catching, not yet preventing)

That is methodological maturity. The architecture is doing its job. The remaining work is implementation hardening — cheapening the catches, raising the gates, tightening the contracts.

The siege felt frustrating. The yield was structural.

— Frontier audit, Session 62, 27 April 2026, Cape Town.
