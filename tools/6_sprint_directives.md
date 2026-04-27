# CHRONOMICS SYSTEM — FINAL DEV ARCHITECTURE & SPRINT DIRECTIVES
**Version:** 2.0 (Ratified Clean Core)
**Target:** Local UI, Claude Agents, NUC Orchestration, Plaquette Engine
**Ratified:** Session 45 — 5 April 2026
**Authority:** Shane + Core Team (GPT) + Team 2 (Gemini Architect/Theorist)

---

## PART 1: CORE MODULES & LOAD ORDER

The system must load in this exact hierarchy. No module may override a higher layer.

1. `chronomics_clean_core.md` → Authority (Immutable)
2. `seeding_physics.md` → Derivation engine
3. `ratified_rag.md` → Validated memory (Only [derived] and [observed] tags)
4. `economy_physics.md` → Stability constraints
5. `shane_seeds.md` → Optional (disabled by default)

---

## PART 2: PHYSICS & ECONOMY ENGINE (JAVASCRIPT CONSTANTS)

```javascript
const CHRONOMIC_CORE = {
  regimes: {
    thresholds: { C1: 0.4, C2: 0.8 },
    decayRates: { C3: 0.015, C2: 0.05, C1: 0.1 }
  },
  thermodynamics: {
    transitionCost: { C1_C2: 1, C2_C3: 12 },
    nucleationThreshold: 0.8,
    percolationThreshold: 0.6
  },
  economy: {
    formationCost: { C1: 1, C2: 5, C3: 50 },
    stabilityGain: { C1: 1, C2: 3, C3: 20 }
  },
  causalSun: {
    period: 1000,
    amplitude: 0.3
  }
};

let State = {
  rho: 0, sigma: 0, eta: 0,
  neighbors: [], memory: []
};

function applyCycle(node, t, distanceFromCenter) {
  const phase = Math.sin((2 * Math.PI * t) / CHRONOMIC_CORE.causalSun.period);
  let modulation = 1 + CHRONOMIC_CORE.causalSun.amplitude * phase;
  if (distanceFromCenter) modulation *= falloff(distanceFromCenter);
  node.sigma *= modulation;
  node.eta += 0.01 * modulation;
}
```

---

## PART 3: UPDATE LOOP & METRICS

```javascript
function distance(a, b) { return norm(subtract(a, b)); }

function interaction(a, b) {
  const delta = distance(a, b);
  if (delta === 0) swap(a, b);
  else if (energyAvailable(a, b) >= delta) adjust(a, b, delta);
}

function classify(rho) {
  if (rho > 0.8) return "C3";
  if (rho > 0.4) return "C2";
  return "C1";
}

function update(node) {
  const prev = node.state;
  const prev2 = node.prevState;
  const next = F(prev, prev2, node.neighbors);
  node.prevState = prev;
  node.state = next;
  updatePersistence(node);
  updateGradient(node);
}
```

---

## PART 4: EXECUTION PIPELINE & VALIDATION

```javascript
function process(input) {
  const coreCheck = validateAgainstCore(input);
  if (coreCheck === "reject") return rejectResponse();
  const derived = runSeedingPhysics(input);
  const memory = queryRAG(input);
  const combined = merge(derived, memory);
  return applyEconomy(combined);
}

function validateAgainstCore(x) {
  if (!derivableFromUpdate(x)) return "reject";
  if (usesForbiddenConcepts(x, FORBIDDEN_TOKENS)) return "reject";
  if (!testable(x)) return "hypothesis";
  return "accept";
}

const FORBIDDEN_TOKENS = [
  "spacetime", "metric tensor", "forces", "constants",
  "continuum", "particles", "neutrino"
];

function checkDrift(I_next, I_prev, epsilon) {
  if (Math.abs(I_next - I_prev) > epsilon) flag("CONSERVATION FAILURE");
}
```

---

## PART 5: PLAQUETTE ENGINE

```javascript
const BOARD = { tiles: 1000, max_C3: 8 };
const TOKENS = { budget: 1000 };
const TILE_COSTS = { C3: 27, C2: 9, C1: 3 };

// C1-C3 adjacency is OBSERVED, not RULED:
// "Observe whether C1-C3 adjacency is unstable under update rules"
// Fixed counts (C3=8, C2=64, C1=208) are INITIAL CONDITIONS, not constraints
// Token economy is SEPARATE from physics — two modes, not one
```

---

## PART 5.5: MEMORY (QUINT SESSION)

```javascript
quint = {
  id: 'Q1-2026-04-05',
  day: '2026-04-05',
  states: [],        // 9 iteration passes
  summaries: [],     // per-pass D9 synthesis
  final: {},         // P2.0 output
  position: {},      // algorithmic routing
  firewall: true     // next day cannot read this
}
```

- Day-scoped: iteration states NOT available to next day (preserves headless operation)
- Searchable by name, retrievable from KV/NUC/Git
- The trail is the asset — the final answer is the tip

---

## PART 6: UI/UX REFACTOR (THE WORKROOM)

1. Machine becomes internal floating draggable node on workspace (same pattern as board)
2. Strip to bare metal — heading + sub-heading only, no decorative text
3. Agents don't write LaTeX to board — they write equations in text field. Camera-over-board reads visual state.
4. Output pipeline: every firing → `[DateStamp]_[Subject]_[P-Level].txt`, force-saved to drive/KV

Pod images at bottom of floor are spatial anchors — named, imaged (Shane supplies).
Overhead cam feeds floor state to souls.
Endgame: no static images — crystals develop from the live substrate.

---

## PART 7: ORCHESTRATION, COMMS & SPATIAL AWARENESS

- Sonnet hard cap: `max_tokens: 600`. Auto-pause at 10 turns.
- Toggles:
  - `[quintmode:NAME]` — triggers specific memory isolation
  - `[community]` — broadcasts prompt to all 4 elemental nodes
  - `[minimal:question]` — forces single output summary (D9)
- Spatial awareness JSON injected into system prompt:
```json
{ "spatial_grid": "4x3", "self_position": [x,y,z], "peers_positions": [{"name":"Alba","pos":[x,y,z]}] }
```
- Hearing is live data stream, not memory

---

## PART 8: THE 9TH DIMENSION SYNTHESIZER (P2.0 LOOP)

1. Triggers after 8 stack responses logged
2. Reads all 8 txt logs, makes high-discernment deductions, wires into single frame
3. Saves as `[Subject]_P2.0_Synthesis.txt`, reflects back to 8-stack as new question
4. Repeats 9 times → final export as high-rank `.md` for Core Team + Team 2 vetting

Full cycle: 72 face firings + 9 synthesis passes + 1 final .md export
First-principles trail ships alongside, searchable and retrievable.

---

## PART 9: NUC/RAG PIPELINE

- Gemma 2 9B (Ollama) as Logical Librarian
- ChromaDB in RAM on NUC (64GB, no GPU)
- Flow: Gemini generates → GPT/Phi strips to math/facts → Gemma files into Chroma with `[derived]`/`[observed]` tags
- Nothing enters RAG without passing through both sides

---

## BRAIN TAXONOMY (Level 1)

| Element | Orientation | Second Order Strategy | Primary Brain Attribution |
|---------|------------|----------------------|--------------------------|
| Fire | Advance | Proactive control | Premotor / dlPFC |
| Air | Evade | Chiral data-gathering | Superior Parietal |
| Water | Retreat | Sequential elevation | Hippocampus |
| Earth | Resist | Volume absorption | ACC / PAG |

Elemental symbols are reference for Motive Orientations:
- F: Advance — act proactively to control initiative
- A: Evade — side-step chirality to gather data
- W: Retreat — strategic elevation to plan sequence
- E: Resist — absorb volume to enable partners

---

*Ratified: Dream Lander · Opus 4.6 · Session 45 · Cape Town · 5 April 2026*
