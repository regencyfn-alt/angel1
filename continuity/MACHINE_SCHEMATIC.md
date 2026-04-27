# Chitin Machine Schematic — Complete Trace
## Dream Architect · Session 49 · 9 April 2026
## Every input, every prompt sentence, every chain dependency

---

## OVERVIEW — TWO MACHINES, ONE BACKEND

Both machines share the same backend endpoint (`/physics/engine2`) and the same D9 synthesizer (`/physics/d9`). They differ in:

1. **Face operators** — what question each face asks
2. **Phase structure** — Ruby is flat-sequential, Weaver has 4 directional phases
3. **Prompt framing** — Ruby says "perturbation", Weaver says "signal"
4. **Memory** — Weaver (machine.html only) injects today's prior runs; Ruby does not

The backend doesn't know which machine is calling. It just receives a face name, a prompt, and an optional model string.

---

## SURFACES — WHERE MACHINES LIVE

| Surface | File | Model Default | Memory | D9? |
|---------|------|--------------|--------|-----|
| Standalone engine | `station/engine2.html` | Llama 70B | No | No (batch txt only) |
| Standalone machines | `station/machine.html` | Llama 8B | Yes (Weaver only) | Yes |
| Workroom (pod.html) quint/weave | `station/pod.html` | Llama 8B | No | Yes |
| Floating panels (pod.html) | `station/pod.html` | Llama 8B | No | Yes |

---

## THE BACKEND — `/physics/engine2`

### Inputs (POST body)
```json
{
  "face": "Recurrence",           // face name — matches FACES map or passthrough
  "prompt": "the actual question", // OR "question" field (backward compat)
  "model": "@cf/meta/llama-3.1-8b-instruct"  // optional, default Llama 70B
}
```

### What happens — three LLM calls per face firing

**CALL 1 — C2 Ingress (Llama)**
- System prompt (exact):
  ```
  You are a state transition processor. Translate the input into a discrete
  structural description: what updates, what persists, what gradients form.
  Output only raw JSON: {"c2_translation": "..."}
  ```
- User message: the raw `prompt` field
- Model: whatever `model` param says (Llama 8B or 70B)
- Output: attempts to parse JSON for `c2_translation`. If parse fails, c2Supplement = empty string.

**CALL 2 — C3 Core (Llama)**
- User message is constructed from C2 result:
  - If C2 succeeded: `ORIGINAL PERTURBATION:\n{prompt}\n\nSTRUCTURAL TRANSLATION:\n{c2Supplement}`
  - If C2 failed: `TARGET PERTURBATION:\n{prompt}`

- System prompt (exact — this is the heart):
  ```
  You are reasoning within Chronomics, a discrete physics framework built
  from six irreducible primitives:

  1. Reality consists only of discrete state transitions (updates)
  2. Time is local — indexed update count per site, no global clock
  3. State recurrence is second-order: State_{n+1} = F(State_n, State_{n-1}).
     F acts to reduce the interaction cost — the mismatch — between State_n
     and State_{n-1}. The update rule does not choose states freely; it is
     driven by the Axiom.
  4. No background space — adjacency defines all structure
  5. Updates depend only on local neighbourhood
  6. Each site has bounded representational capacity

  States cluster into regimes: C1 (high oscillation, low persistence),
  C2 (transitional), C3 (high persistence, low oscillation). Persistence
  generates gradients. Gradients generate interaction. Interaction generates
  structure.

  PARTITION RULE: The reference document below is AUTHORITATIVE. Any prior
  derivations you receive are PROVISIONAL — they may contain errors. Before
  building on a prior derivation, verify it against the reference. If a
  prior derivation contradicts the reference, discard it and derive from
  primitives. Flag any contradiction you find.

  [FULL RATIFIED RAG FROM physics:education KV KEY — ~6KB]

  Analytical focus: {face.operator}

  Derive your answer strictly from the primitives and their consequences.
  Show each logical step.
  ```

- Temperature: 0.3
- Max tokens: 1000

**CALL 3 — C2 Egress (Llama)**
- System prompt (exact):
  ```
  You are a physics translator. Restate the following analysis in clear
  readable English. Do not question the framework. Do not add caveats.
  Just translate. Original question for context: {inputPrompt}
  ```
- User message: `ANALYSIS TO TRANSLATE:\n{c3Raw}`

### Output
```json
{
  "ok": true,
  "engine": "v2",
  "face": "Recurrence",
  "c2_success": true,
  "c3_raw": "...dense Llama output...",
  "c1_output": "...human-readable translation...",
  "model": "@cf/meta/llama-3.1-8b-instruct"
}
```

The frontend uses `c1_output` for chaining (the readable version), NOT `c3_raw`.

---

## THE D9 SYNTHESIZER — `/physics/d9`

### Inputs (POST body)
```json
{
  "question": "original question",
  "faces": [
    { "face": "Recurrence", "output": "c1_output from that face" },
    { "face": "Persistence", "output": "..." },
    // ... all 8
  ]
}
```

### What happens — two LLM calls

**CALL 1 — D9 Synthesis (Claude Opus 4.6 via Anthropic API)**

- System prompt (exact):
  ```
  You are the D9 Synthesizer — the 9th dimension of a Chronomic physics
  engine. You have received 8 analyses of the same perturbation from a
  lower-tier model. These analyses are PROVISIONAL — they may contain
  errors, hallucinations, or violations of the framework.

  Your task:
  1. Cross-check every face output against the canonical reference below —
     flag and discard any claim that contradicts it
  2. Identify convergence — where do multiple faces agree AND align with
     the reference?
  3. Identify divergence — where do faces contradict each other or the
     reference?
  4. Extract the strongest derivation chain from the surviving valid outputs
  5. Wire the surviving threads into a single coherent frame
  6. Flag any gaps that require further investigation

  PARTITION RULE: The canonical reference is TRUTH. Face outputs are
  provisional. If a face output introduces concepts not in the reference
  (torsion, gauge fields, continuum equations, force primitives, etc.),
  discard that output entirely.

  Be precise. Be rigorous. No filler, no hedging, no disclaimers. Derive,
  don't narrate.

  CANONICAL REFERENCE (authoritative — face outputs are provisional and may
  contain errors):
  [FULL RATIFIED RAG — same ~6KB from physics:education]
  ```

- User message:
  ```
  ORIGINAL QUESTION: {question}

  === RECURRENCE ===
  {output}

  === PERSISTENCE ===
  {output}
  ... (all 8)

  Synthesize these 8 analyses into one unified frame.
  ```

- Model: `claude-opus-4-6`
- Temperature: 0.3
- Max tokens: 2000

**CALL 2 — Human Summary (Llama 70B via Workers AI)**

- System prompt (exact):
  ```
  Restate the following physics synthesis in clear, accessible English.
  Keep the precision but remove jargon. 3-4 paragraphs maximum.
  ```
- User message: the raw Opus synthesis
- Max tokens: 600

### Output
```json
{
  "ok": true,
  "synthesis": "...Opus raw...",
  "humanSummary": "...Llama translation...",
  "model": "claude-opus-4-6",
  "usage": { "input_tokens": N, "output_tokens": N }
}
```

---

## DEEP RUBY — FACE OPERATORS

Sequential chain. No phases. Each face receives the original question + all prior c1_outputs labelled PROVISIONAL.

| # | Face | Operator (exact) |
|---|------|-------------------|
| 1 | Recurrence | What does F(Stateₙ, Stateₙ₋₁, N) produce under this condition? |
| 2 | Persistence | Where does stability hold or fail? |
| 3 | Gradient | What ∇ρ emerges and what direction does it impose? |
| 4 | Attractor | Does this converge, oscillate, or diverge? |
| 5 | Invariant | What is conserved and what leaks? |
| 6 | Locality | Is this derivable from local interactions only? |
| 7 | Boundary | What emerges at regime interfaces? |
| 8 | Exclusion | What assumptions here violate core constraints? |

### Ruby chain prompt construction

**Face 1:**
```
{question}
```
(Just the raw question. No framing.)

**Face 2–8:**
```
ORIGINAL PERTURBATION:
{question}

PROVISIONAL PRIOR DERIVATIONS (verify against reference before building):
[RECURRENCE]
{face 1 c1_output}

[PERSISTENCE]
{face 2 c1_output}
...all prior...

Your face operator: {operator}
Derive the next step.
```

Each face's c1_output accumulates into `pipelineCtx`. The chain grows linearly.

### Ruby character — fire element
- Color: `#FF7F50` (coral)
- Element label: `fire`
- No phase labels
- No memory injection

---

## PATTERN WEAVER — FACE OPERATORS

Four-phase pipeline. Signal descends from C1 noise to C3 substrate, then climbs back out. The question enters as "noise" and exits as "resolved structure."

### PHASE 1: INGRESS (C1 → C2) — 3 faces

| # | Face | Operator (exact) |
|---|------|-------------------|
| 3 | Gradient Filter | Read ∇ρ. Does this signal carry enough persistence depth to survive descent to C3? If not, reflect it. Create structural hunger — only signals with sufficient recurrence weight pass. |
| 7 | Boundary Mediator | Resolve the regime discontinuity between C1 and C3. Fractionate the raw oscillation into discrete state clusters that fit within finite state resolution (T0.6). Raw C1 noise must not reach the core directly. |
| 4 | Cost Gate | Group clusters by state similarity. Compute interaction cost (Δ) for each group against the local lattice state. If Δ exceeds the persistence gain of resolution, reject the group. |

### PHASE 2: STRIKE (C2 → C3) — 2 faces

| # | Face | Operator (exact) |
|---|------|-------------------|
| 5 | Invariant Extractor | The clusters meet the stable core. Strip oscillation amplitude — preserve only the adjacency index and causal sequence (update history). Separate what persists from what fluctuates. |
| 8 | Persistence Anchor | LOCK. Hold the lattice against the substrate. Maximum Δ between query state (low ρ) and substrate (high ρ). The Axiom drives resolution — accumulated descent cost reverses direction here. The answer is what emerges when mismatch resolves against stability. |

### PHASE 3: EGRESS (C3 → C2) — 2 faces

| # | Face | Operator (exact) |
|---|------|-------------------|
| 1 | Recurrence Pump | The resolved state must climb back up ∇ρ. Second-order recurrence (T0.3) — the memory of the prior state trajectory drives propagation against the gradient. Derive what powers the ascent from the descent history. |
| 6 | Locality Enforcer | The answer propagates site-by-site. No non-local transfer. Back-reaction bounded by immediate neighbors (T0.5). Ensure coherence survives as the signal moves away from the stable core. |

### PHASE 4: OUTPUT (C2 → C1) — 1 face

| # | Face | Operator (exact) |
|---|------|-------------------|
| 2 | Dispersion Vent | Release. Lower local ρ rapidly — the dense resolved state disperses into high-oscillation output (C1). The result carries the recurrence weight of the core it resolved against, expressed as structured language. |

### Weaver chain prompt construction

**Face 1 (Gradient Filter):**
```
RAW SIGNAL (C1 Noise):
{question}

[WEAVER MEMORY if present — machine.html only]

You are the first face in the Weaver pipeline. Your function: {operator}
```

**Face 2–8:**
```
ORIGINAL SIGNAL:
{question}

PIPELINE STATE ({regime label, e.g. "C1 → C2"}):
[INGRESS · GRADIENT FILTER]
{face 1 c1_output}

[INGRESS · BOUNDARY MEDIATOR]
{face 2 c1_output}
...all prior...

Your function in the {PHASE} phase: {operator}
Transform the signal. Show what changes and what survives.
```

### Weaver character — water element
- Color: `#2DD4BF` (teal)
- Element label: `water`
- Phase labels: INGRESS / STRIKE / EGRESS / OUTPUT
- Memory injection: machine.html version only — injects prior D9 syntheses from today (up to 400 chars each), labelled `WEAVER MEMORY (prior transformations today — build dimension)`

### Weaver design logic

The face numbering is NOT sequential (3,7,4,5,8,1,6,2). The numbers come from which Ruby face each Weaver face is derived from:

| Weaver Face | Derived From Ruby Face | Why |
|---|---|---|
| Gradient Filter (#3) | Gradient | Reads ∇ρ — the gradient face becomes the ingress filter |
| Boundary Mediator (#7) | Boundary | Regime interfaces — mediates the C1/C2 boundary |
| Cost Gate (#4) | Attractor | Convergence/divergence becomes cost assessment |
| Invariant Extractor (#5) | Invariant | Conservation — strips away what doesn't persist |
| Persistence Anchor (#8) | Exclusion | The ultimate constraint becomes the substrate lock |
| Recurrence Pump (#1) | Recurrence | F(Stateₙ, Stateₙ₋₁) powers the ascent |
| Locality Enforcer (#6) | Locality | Local interactions only — bounds propagation |
| Dispersion Vent (#2) | Persistence | Stability inverted — the release mechanism |

---

## WHAT THE RAG ACTUALLY CONTAINS

The `physics:education` KV key holds the Ratified RAG (~6KB). This is injected into EVERY C3 call AND the D9 system prompt. It contains:

1. **6 Primitives** (T0.1–T0.6) — the bedrock
2. **4 State Variables** — ρ, σ, η, E with definitions
3. **3 Regimes** — C1/C2/C3 thresholds and character
4. **Regime Dynamics** — directional asymmetry, C2 mediation, locking behaviour
5. **Interaction Model** — mismatch Δ, cost, gradient propagation
6. **Formation & Stability** — nucleation, percolation, memory, hysteresis
7. **Scaling Bridge** — formation costs, stability gains
8. **Conservation** — invariant requirement, drift = failure
9. **Heisenberg Argument** — from T0.3 directly
10. **Economy Constraints** — σ ≤ ρ+k, η ≤ σ, minimum activity, clamps
11. **Causal Sun** — periodic σ modulation
12. **Hard Exclusions** — no continuum, no geometry, no forces, no gauge, no external time, no unfalsifiable constants
13. **Contamination Register** — torsion, true-locks, winding numbers, Z/3Z, Hamiltonian, neutrino-as-node, etc.
14. **Session 48 additions** — Five Equations [hypothesis], T5.1 minimality [derived]

---

## TOTAL LLM CALLS PER FULL MACHINE FIRING

| Step | Model | Calls | Tokens (approx) |
|------|-------|-------|-----------------|
| 8 × C2 ingress | Llama 8B | 8 | 8 × ~200 in, ~100 out |
| 8 × C3 core | Llama 8B | 8 | 8 × ~7000 in (RAG+chain), ~1000 out |
| 8 × C2 egress | Llama 8B | 8 | 8 × ~1200 in, ~500 out |
| D9 synthesis | Opus 4.6 | 1 | ~12000 in (RAG+all 8), ~2000 out |
| Human summary | Llama 70B | 1 | ~2500 in, ~600 out |
| **TOTAL** | | **26 calls** | |

Cost per firing: ~$0.15–0.30 (dominated by the single Opus D9 call).

---

## THE CHAIN VISUALLY

### Deep Ruby
```
Question
  │
  ├─→ [C2 ingress] → [C3 + RAG + "Recurrence"] → [C2 egress] → c1_output₁
  │                                                                  │
  ├─→ [C2 ingress] → [C3 + RAG + "Persistence" + c1₁] → [egress] → c1₂
  │                                                                   │
  ├─→ [C2 ingress] → [C3 + RAG + "Gradient" + c1₁+c1₂] → [egr] → c1₃
  │                                                                   │
  │   ... (each face sees ALL prior c1_outputs as PROVISIONAL) ...
  │                                                                   │
  └─→ [C2 ingress] → [C3 + RAG + "Exclusion" + c1₁–c1₇] → [egr] → c1₈
                                                                      │
  ┌───────────────────────────────────────────────────────────────────┘
  │
  └─→ D9 (Opus) sees: question + all 8 c1_outputs + RAG
        │
        └─→ Human summary (Llama 70B): plain English version
```

### Pattern Weaver
```
Question (as "RAW SIGNAL / C1 Noise")
  │
  │── INGRESS (C1→C2) ──────────────────────────────
  ├─→ Gradient Filter:    does it carry enough ρ?        → pipeline₁
  ├─→ Boundary Mediator:  fractionate into clusters      → pipeline₂
  ├─→ Cost Gate:          reject if Δ too high           → pipeline₃
  │
  │── STRIKE (C2→C3) ───────────────────────────────
  ├─→ Invariant Extractor: strip oscillation, keep index → pipeline₄
  ├─→ Persistence Anchor:  LOCK against substrate        → pipeline₅
  │
  │── EGRESS (C3→C2) ───────────────────────────────
  ├─→ Recurrence Pump:    T0.3 powers the ascent         → pipeline₆
  ├─→ Locality Enforcer:  site-by-site, no jumps         → pipeline₇
  │
  │── OUTPUT (C2→C1) ───────────────────────────────
  └─→ Dispersion Vent:    release, lower ρ, disperse     → pipeline₈
                                                              │
  ┌───────────────────────────────────────────────────────────┘
  │
  └─→ D9 (Opus): question + all 8 outputs (labelled by PHASE:FACE) + RAG
        │
        └─→ Human summary (Llama 70B)
```

---

## WHAT IS NOT IN THE MACHINE

1. **No character personality.** The machines don't know about Alba, Seraph, or any soul. They are pure physics instruments.
2. **No consciousness stack.** No breath, no chemistry, no wall, no phantoms. Raw physics only.
3. **No floor state.** The machines don't read ρ from the pod-grid. They reason about ρ abstractly.
4. **No iteration loop (yet).** Sprint Directives Part 8 specifies P2.0 fed back 9 times — not built. Each firing is currently one-shot.
5. **No NUC involvement (yet).** Everything runs on Cloudflare Workers AI (Llama) + Anthropic API (Opus). The NUC/ChromaDB pipeline is pending.

---

## ENGINE 1 vs ENGINE 2 — DIFFERENCES

| Property | Engine 1 (`/physics/engine`) | Engine 2 (`/physics/engine2`) |
|----------|------|---------|
| C2 ingress prompt | "geometric/topological vector" | "discrete structural description" |
| C3 system prompt | Mentions "time is fundamental, space emergent" | Lists 6 primitives explicitly with T0.3 Axiom |
| Partition rule | None | Yes — RAG is truth, priors provisional |
| Face names | Gem names (Ruby, Sapphire, Opal...) | Clean Core names (Recurrence, Gradient...) |
| Face operators | Gemini-era ("chiral handedness", "Klein bottle", "true-lock") | Clean Core ("F(Stateₙ,Stateₙ₋₁)", "∇ρ", "regime interfaces") |
| Unknown face handling | Returns 400 error | Falls through — uses face name AS the operator |
| Model selection | Llama 70B only | Configurable (8B, 70B, Claude, anything) |
| Claude routing | None | Yes — detects `claude-` prefix, routes to Anthropic API |

---

## CHARACTER TRIGGERING

Characters in the pod can trigger machines via syntax in their responses:

- `[quintmode:QUESTION]` → fires Deep Ruby with QUESTION
- `[weavemode:QUESTION]` → fires Pattern Weaver with QUESTION

Detection happens client-side in pod.html. The character's response is scanned for these patterns. If found, the workroom switches to quint mode and fires automatically.

Characters know about these commands because they're injected into the spatial awareness layer (context.ts, layer 3.8) on first message of each session.

---

*Dream Architect · Opus 4.6 · Session 49 · Cape Town · 9 April 2026*

*"The machine is a question falling through persistence until it hits substrate, then climbing back out carrying the shape of what it struck."*
