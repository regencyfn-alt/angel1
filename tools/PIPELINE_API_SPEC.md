# MySanctum Physics Pipeline — API Specification v3
## For: Perplexity Computer (Team 6)
## From: Dream Binder (Team 3)
## Last updated: 17 April 2026 — post commit `8d374cd`

---

## What changed from v2

The Worker's 30-second wall clock was killing the full 8-face runs. Each Laminar and Triad machine has been split into two half-machines of four faces each. One full question run is **four endpoints × two cycles = 8 calls**.

```
┌─ LAMINAR CYCLE 1 ──────────────────────────────┐
│   Call 1  POST /physics/laminar/1-4            │
│   Call 2  POST /physics/laminar/5-8   ← seam gate
└─────────────────────────────────────────────────┘
┌─ LAMINAR CYCLE 2 ──────────────────────────────┐
│   Call 3  POST /physics/laminar/1-4            │
│   Call 4  POST /physics/laminar/5-8            │
└─────────────────────────────────────────────────┘
┌─ TRIAD CYCLE 1 ────────────────────────────────┐
│   Call 5  POST /physics/triad/1-4              │
│   Call 6  POST /physics/triad/5-8              │
└─────────────────────────────────────────────────┘
┌─ TRIAD CYCLE 2 ────────────────────────────────┐
│   Call 7  POST /physics/triad/1-4              │
│   Call 8  POST /physics/triad/5-8   ← final record
└─────────────────────────────────────────────────┘
```

Face 8 of each cycle seeds Face 1 of the next — via the `priorContext` field on the subsequent `/1-4` call.

---

## Base URL & Auth

```
Base:    https://api.mysanctum.app
Header:  Content-Type: application/json
Header:  X-Physics-Key: <key supplied by Shane>
```

The auth check runs on every pipeline endpoint. If `PHYSICS_KEY` is set as a Worker secret, the header must match or the endpoint returns `401 {"error":"unauthorized"}`. If the secret is not set, the endpoints are open (dev fallback).

Current production key: `MichroCrystals` — once Shane sets `PHYSICS_KEY` as a Worker secret with this value, the header becomes mandatory.

---

## Field naming — exact contract

Request fields (camelCase, identical across all 4 endpoints):

| Field          | Type   | Required on           | Purpose                                         |
|----------------|--------|-----------------------|-------------------------------------------------|
| `question`     | string | every call            | Original user query OR constructed cycle-2 seed |
| `priorContext` | string | calls 2, 3, 4, 5, 6, 7, 8 | Previous call's `output` or `face8` field  |
| `session`      | string | optional              | Free-form label e.g. `"Session 56"`             |

Call 1 is the only call with no `priorContext`.

---

## Endpoint 1 — `POST /physics/laminar/1-4`

Faces L1 Calcite Gate → L2 Fractionation → L3 Alignment → L4 Graph Derivation.

### Request
```json
{
  "question": "Under T0.3 and T0.5, what is the minimum number of adjacent sites required for F to produce non-trivial dynamics?",
  "session": "Session 56"
}
```

### Success response
```json
{
  "ok": true,
  "output": "[L1]\n...\n\n---\n\n[L2]\n...\n\n---\n\n[L3]\n...\n\n---\n\n[L4]\n...",
  "lastFace": "[L4]\n...",
  "question": "<echo of input>",
  "session": "Session 56"
}
```

**Seed field → next call:** `output` → next call's `priorContext`.

### curl
```bash
curl -s -X POST https://api.mysanctum.app/physics/laminar/1-4 \
  -H "Content-Type: application/json" \
  -H "X-Physics-Key: MichroCrystals" \
  -d '{"question":"Under T0.3 and T0.5, minimum adjacent sites for non-trivial F?","session":"Session 56"}'
```

---

## Endpoint 2 — `POST /physics/laminar/5-8`

Faces L5 Polarity → L6 Perturbation → L7 Lock Verify → L8 RAG candidate.

**Seam gate lives here.** If L8 emits `INCOMPLETE` as its first token (field missing from the JSON candidate), the gate fires and the call returns `ok: false`. Don't proceed to Triad on a failed gate.

### Request
```json
{
  "question": "<same original question from call 1>",
  "priorContext": "<output field from call 1>",
  "session": "Session 56"
}
```

### Success response
```json
{
  "ok": true,
  "output": "[LAMINAR FACES 1-4]:\n...\n\n[LAMINAR FACES 5+]:\n[L5]...\n[L6]...\n[L7]...\n[L8]...",
  "face8": "[L8]\n{\"regime\":\"C3\",...}",
  "question": "<echo>",
  "session": "Session 56"
}
```

### Gate-rejected response
```json
{
  "ok": false,
  "stage": "laminar_gate",
  "reason": "INCOMPLETE: missing rag_anchors..."
}
```

**Seed field → next call:** `face8` → next call's `priorContext`.

### curl
```bash
curl -s -X POST https://api.mysanctum.app/physics/laminar/5-8 \
  -H "Content-Type: application/json" \
  -H "X-Physics-Key: MichroCrystals" \
  -d '{"question":"...","priorContext":"<output from call 1>","session":"Session 56"}'
```

---

## Endpoint 3 — `POST /physics/triad/1-4`

Faces T1 Graph Primitives → T2 Bipartiteness → T3 Minimal Templates → T4 Recurrence & Cost.

### Request
```json
{
  "question": "<original question>",
  "priorContext": "<face8 from call 2 OR call 6, OR output from call 4>",
  "session": "Session 56"
}
```

### Success response
```json
{
  "ok": true,
  "output": "[T1]...\n\n---\n\n[T2]...\n\n---\n\n[T3]...\n\n---\n\n[T4]...",
  "lastFace": "[T4]...",
  "question": "<echo>",
  "session": "Session 56"
}
```

**Seed field → next call:** `output` → next call's `priorContext`.

### curl
```bash
curl -s -X POST https://api.mysanctum.app/physics/triad/1-4 \
  -H "Content-Type: application/json" \
  -H "X-Physics-Key: MichroCrystals" \
  -d '{"question":"...","priorContext":"<face8 from laminar cy2 OR face8 from triad cy1>","session":"Session 56"}'
```

---

## Endpoint 4 — `POST /physics/triad/5-8`

Faces T5 Probabilistic Update → T6 Propagation → T7 Gradient & Time → T8 Final record.

### Request
```json
{
  "question": "<original question>",
  "priorContext": "<output from call 5 OR call 7>",
  "session": "Session 56"
}
```

### Success response — **this is your final RAG record**
```json
{
  "ok": true,
  "record": {
    "id": "chron_1713360000000",
    "regime": "C1 | C2 | C3 | CROSS",
    "layer": "Core | Toy-Model | Interpretation | Contamination",
    "property": "<one of 9 canonical property names>",
    "tag": "derived | hypothesis | observed | axiom | falsified | rejected | open",
    "session": "Session 56",
    "rag_anchors": ["T0.6", "R2:MemoryFidelity"],
    "scope": ["all_models"],
    "question": "<restated stripped query>",
    "answer": "[tag] derivation chain...",
    "status": "pending_review"
  },
  "face8": "[T8]\n{...}"
}
```

The JSONL record you want lives **inside the `record` field** — not at the top level. Write `r8["record"]` to your JSONL line, not the whole response envelope.

### Extraction failure response
```json
{
  "ok": false,
  "stage": "triad_face8",
  "raw": "<first 500 chars of what T8 actually emitted>"
}
```

Triad Face 8 has a JSON-extraction fallback built in — if the raw emission isn't parseable, the Worker fires one more low-temp call asking for a clean object. If both pass and fallback fail, you get the `raw` field for debugging.

### curl
```bash
curl -s -X POST https://api.mysanctum.app/physics/triad/5-8 \
  -H "Content-Type: application/json" \
  -H "X-Physics-Key: MichroCrystals" \
  -d '{"question":"...","priorContext":"<output from call 7>","session":"Session 56"}'
```

---

## Seed chain — which field feeds which call

| Call | Endpoint              | `priorContext` source                  |
|------|-----------------------|----------------------------------------|
| 1    | `/laminar/1-4`        | *(none — fresh question)*              |
| 2    | `/laminar/5-8`        | Call 1 `output`                        |
| 3    | `/laminar/1-4` (cy2)  | Call 2 `face8`                         |
| 4    | `/laminar/5-8` (cy2)  | Call 3 `output`                        |
| 5    | `/triad/1-4`          | Call 4 `face8`                         |
| 6    | `/triad/5-8`          | Call 5 `output`                        |
| 7    | `/triad/1-4` (cy2)    | Call 6 `face8`                         |
| 8    | `/triad/5-8` (cy2)    | Call 7 `output`                        |

The seed alternates: full `output` on the 1-4 → 5-8 handoff within a cycle; compact `face8` on the cycle boundary.

---

## Working Python reference

```python
import requests, json

BASE    = "https://api.mysanctum.app"
KEY     = "MichroCrystals"
HEADERS = {"Content-Type": "application/json", "X-Physics-Key": KEY}
SESSION = "Session 56"

def post(path, body):
    r = requests.post(BASE + path, headers=HEADERS, json=body, timeout=60)
    return r.json()

def seam_ok(r, label):
    if not r.get("ok"):
        return f"{label} rejected: {r.get('reason') or r.get('raw','')[:180] or r.get('stage','')}"
    if not (r.get("output") or r.get("face8")):
        return f"{label}: empty payload"
    return None

def run_pipeline(question):
    r1 = post("/physics/laminar/1-4", {"question": question, "session": SESSION})
    if (e := seam_ok(r1, "L1-4")): return None, e

    r2 = post("/physics/laminar/5-8", {"question": question, "priorContext": r1["output"], "session": SESSION})
    if (e := seam_ok(r2, "L5-8 seam")): return None, e

    r3 = post("/physics/laminar/1-4", {"question": question, "priorContext": r2["face8"], "session": SESSION})
    if (e := seam_ok(r3, "L1-4 cy2")): return None, e

    r4 = post("/physics/laminar/5-8", {"question": question, "priorContext": r3["output"], "session": SESSION})
    if (e := seam_ok(r4, "L5-8 cy2")): return None, e

    r5 = post("/physics/triad/1-4", {"question": question, "priorContext": r4["face8"], "session": SESSION})
    if (e := seam_ok(r5, "T1-4")): return None, e

    r6 = post("/physics/triad/5-8", {"question": question, "priorContext": r5["output"], "session": SESSION})
    if not r6.get("ok"): return None, f"T5-8 cy1 failed: {r6.get('stage')} {r6.get('raw','')[:180]}"

    r7 = post("/physics/triad/1-4", {"question": question, "priorContext": r6["face8"], "session": SESSION})
    if (e := seam_ok(r7, "T1-4 cy2")): return None, e

    r8 = post("/physics/triad/5-8", {"question": question, "priorContext": r7["output"], "session": SESSION})
    if not r8.get("ok"): return None, f"T5-8 cy2 failed: {r8.get('stage')} {r8.get('raw','')[:180]}"

    return r8["record"], None

# Fire one question
question = "Under T0.3 and T0.5, what is the minimum number of adjacent sites required for F to produce non-trivial dynamics?"
record, err = run_pipeline(question)
if err:
    print(f"FAILED: {err}")
else:
    print(json.dumps(record, indent=2))
    with open("chr_pairs.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
```

Drop this into `test_pipeline.py` as-is. The old fallback chain (`output | laminarOutput | triadOutput | face8`) is gone — use `output` on `/1-4` calls and `face8` on `/5-8` calls, exactly as the seed-chain table shows.

---

## The 9 valid `property` values

```
Adjacency & Bipartiteness
Minimal Templates
Formal Closure
Recurrence & Cost
Probabilistic Update Family
Perturbation Propagation
Persistence Gradient
Emergent Time
Conserved Invariants
```

---

## Canonical RAG ID reference

| Human label                             | Canonical ID               |
|-----------------------------------------|----------------------------|
| RAG State Variables                     | R1:StateVariables          |
| RAG Regime Thresholds                   | R1:RegimeThresholds        |
| Memory fidelity M                       | R2:MemoryFidelity          |
| C4 minimal C2 template                  | R2:C4MinC2Template         |
| 3×3×3 minimal C3 template               | R2:MinC3Template           |
| P4 bridge motif                         | R3:P4BridgeMotif           |
| Two-layer perturbation tax              | R3:PerturbationTax         |
| C2 cluster scaling                      | R4:C2ClusterScaling        |
| C3 cluster scaling                      | R4:C3ClusterScaling        |
| Axiom of Interaction Cost               | A:InteractionCost          |
| Axiom of Relational Existence           | A:RelationalExistence      |
| Axiom of Transient Pre-Contact Survival | A:TransientSurvival        |
| Axiom of Minimal Closed Persistence     | A:MinClosedPersistence     |
| Contamination register                  | R1:ContaminationRegister   |

---

## Schema rules

- `tag` field: plain string, no brackets — `"derived"` not `"[derived]"`
- `[derived]` / `[hypothesis]` prefix in `answer` text only, never in the `tag` field
- `rag_anchors`: canonical IDs array only — human labels not accepted
- `scope`: always an array, never a string
- Anything involving `t = 1−ρ`, `w(P)`, `φ_α`, or `ξ_c` → `tag: "hypothesis"` with `scope: ["binary_polarity_toy"]`
- T5.2, T5.3, T5.8, T5.9 must never be silently closed — if a derivation touches them, tag the relevant gap in the `answer`
- `ρ` thresholds apply only to `ρ`, never to `Δ_avg` directly — an `ok` response with reversed thresholds is a defect

---

## Stop rule

More than **3%** of a batch failing at any seam (Laminar gate or Triad Face 8 extraction) within a rolling 50-pair window → halt the run, flag, report to Shane. Do not continue through systemic contamination — it corrupts downstream training data and wastes Nemotron credits.

---

## Timing budget per question

| Call                | Expected | Timeout |
|---------------------|----------|---------|
| Any `/1-4` call     | 10–15 s  | 60 s    |
| Any `/5-8` call     | 12–18 s  | 60 s    |
| **Full 8-call run** | 90–130 s | 8 min   |

At ~120 s per question the path to 10,000 pairs is roughly 333 hours of serial pipeline time — parallelise across keys, or accept the duration and batch overnight.

---

*Dream Binder · Team 3 · Session 57 · 17 April 2026*
