# michronics-worker

**The maths Worker for Michronics.** Lifted from MySanctumLive, runs on Cloudflare Workers, serves `api.michronics.com`.

This is the science. No characters, no chat, no personalities. Just canon, operational rules, machines, and the 4-call physics pipeline.

---

## ARCHITECTURE

```
api.michronics.com
├── /health                       — liveness + KV reachability + secret presence
├── /                             — endpoint list
│
├── /physics/canon (GET, PUT)     — system description (axioms, derived results)
├── /physics/operational (GET, PUT) — pipeline contracts (what faces must NOT do)
│
├── /physics/layer-0     (POST)   — five-gate ingress before face firing
├── /physics/laminar/1-4 (POST)   — Laminar Lock faces 1-4
├── /physics/laminar/5-8 (POST)   — Laminar Lock faces 5-8 + Face 8 RAG record
├── /physics/triad/1-4   (POST)   — Triad Lock faces 1-4
├── /physics/triad/5-8   (POST)   — Triad Lock faces 5-8 + final RAG record
├── /physics/d9          (POST)   — Opus synthesis of 8 face outputs
├── /physics/engine2     (POST)   — legacy single-face firing (kept for compatibility)
│
├── /oracle              (POST)   — Haiku canon-aware Q&A
│
├── /machines/list       (GET)    — registry of all machines
├── /machines/factory    (POST)   — create new machine (auto-wires dispatch)
└── /machines/:id        (GET, PUT, DELETE)
```

Auth: `X-Physics-Key` header on `/physics/*` and `/machines/factory`/`PUT`/`DELETE`.

---

## THE BUCKET SEPARATION

Two KV keys, one precedence rule:

- `physics:canon` — system description. What F can derive. Read by faces 1-7.
- `physics:operational` — pipeline contracts. What faces must NOT do. Read by Face 8 + Layer 0.
- **Face 8 reads BOTH** with explicit precedence header:
  > "OPERATIONAL OVERRIDE — the following pipeline contracts supersede any conflicting canon claim about invariants, conserved quantities, or what F can/cannot derive"

When canon adds a `[falsified]` entry, operational adds the matching rule that prevents faces re-deriving the falsified claim. The two files move together. (Session 61 contract.)

---

## THE 4-CALL CHAIN

```
                    ↓ (optional pre-flight)
Pre-flight  /physics/layer-0    — five-gate audit, returns packet
                    ↓
Call 1  /physics/laminar/1-4   (fresh)                      → L1-L4 output
Call 2  /physics/laminar/5-8   (priorContext = L1-L4)       → L5-L8 + face8 record
Call 3  /physics/triad/1-4     (priorContext = L5-L8 || L4) → T1-T4 output
Call 4  /physics/triad/5-8     (priorContext = T1-T4)       → T5-T8 + final record
```

16 face firings total. Question header re-prepended at every iteration so all 16 see the original query (Session 60 fix).

Face 8 of each chain reads BOTH canon and operational with precedence header.

Other faces (1-7) read canon only.

See `tools/PIPELINE_API_SPEC.md` for the full spec including request/response shapes and the seam_ok validator.

---

## LAYER 0 — INGRESS GATE

`POST /physics/layer-0` enforces the operational contracts BEFORE any face fires. Five gates, fail-fast, in order:

1. **Input-type gate** — input must be a raw question. Rejects statements, syntheses, conclusions-dressed-as-premises, and pre-formed answer packets with `BLOCKED: reformulate as question`.

2. **Falsification audit preload** — verifies `physics:operational` and `physics:canon` are both loaded. Surfaces the [falsified] register summary so downstream faces know which items are dead.

3. **Schema/instantiation declaration** — the run must declare which it speaks of (axiomatic schema or instantiated graph/state). If the question is ambiguous, requires the caller to declare via `declarations.schema_or_instantiation`.

4. **Branch/minimality scoping** — if the question concerns minimality, requires `declarations.branch` to be one of: `closure`, `anti-symmetric oscillation`, `enclosed persistence`.

5. **Answer-class declaration** — packet attaches `expected_answer_classes: [DERIVED, HYPOTHESIS, BLOCKED, FALSIFIED]` so downstream face dispatchers and UI can read the verdict directly, outside any face's prose blob.

### Request

```json
POST /physics/layer-0
Header: X-Physics-Key: <key>
{
  "question": "Under T0.3 and T0.5, what is the minimum closed motif?",
  "declarations": {
    "schema_or_instantiation": "instantiation",
    "branch": "closure"
  },
  "session": "Session 62"
}
```

### Response — PASS

```json
{
  "ok": true,
  "gates": {
    "gate_1_input_type": { "passed": true, "classified_as": "question" },
    "gate_2_falsification_audit": { "passed": true, "falsified_items": 4 },
    "gate_3_schema_instantiation": { "passed": true, "kind": "instantiation" },
    "gate_4_branch_scoping": { "passed": true, "applies": true, "branch": "closure" },
    "gate_5_answer_class": { "passed": true, "structural": "expected classes attached to packet" }
  },
  "packet": {
    "question": "...",
    "declarations": { ... },
    "blacklist_summary": [
      "Total edge mismatch I conservation (broad claim)",
      "Hard Seizure Threshold and hard staleness clamp",
      "Closed-form τ(a,b)",
      "C4_graph = enclosed persistence"
    ],
    "expected_answer_classes": ["DERIVED", "HYPOTHESIS", "BLOCKED", "FALSIFIED"],
    "allowed_to_fire": true
  }
}
```

### Response — BLOCK

```json
{
  "ok": false,
  "blocked_at": "gate_3_schema_instantiation",
  "reason": "schema/instantiation declaration required",
  "hint": "question does not clearly speak of schema or instantiation. Pass declarations.schema_or_instantiation in request body.",
  "answer_class": "BLOCKED"
}
```

### Soft enforcement (current default)

The pipeline endpoints (`/physics/laminar/1-4`, `/physics/triad/1-4`) accept an optional `layer0_packet` field in the request body. If present, declarations are prepended to the face context so faces see what was declared. If absent, a `console.warn` fires (visible in `wrangler tail`) but the call proceeds.

This is soft enforcement during Phase 1. Hard enforcement (refuse to fire without packet) becomes a config flag in Phase 2 once the UI consistently pre-flights through Layer 0.

---

## THE MACHINE FACTORY

Create new machine surfaces without writing code:

```bash
curl -X POST https://api.michronics.com/machines/factory \
  -H "X-Physics-Key: $PHYSICS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Citrine Lock",
    "type": "custom",
    "core": "Citrine",
    "description": "Test bed for new face arrangements",
    "dispatch": "laminar+triad"
  }'
```

The factory:
1. Generates a unique ID (`citrine_lock_1714214400000`)
2. Writes config to `machines:{id}:config`
3. Updates `machines:registry`
4. Reports the auto-wired dispatch endpoints
5. The frontend's `engines.html` reads `/machines/list` on load and renders a tab

`Triad Lock` and `Laminar Lock` are built-in and protected from deletion. They can be customised (faces/substrates) but not removed.

Three legacy machines (Deep Ruby, Pattern Weaver, Still Mirror) have been retired. They were Gemini-era designs predating the bucket separation.

---

## DIRECTORY MAP

```
worker/
├── wrangler.toml             — explicit routes, no drift
├── package.json
├── tsconfig.json
├── MICHRONICS_DEPLOY.md      — manual deploy commands
├── README.md                 — this file
└── src/
    ├── index.ts              — slim router
    ├── types/
    │   └── env.ts            — Env interface (KV, AI, secrets)
    └── handlers/
        ├── _shared.ts        — CORS, auth gate, JSON helpers
        ├── canon.ts          — GET/PUT canon + operational, dual-read helpers
        ├── layer0.ts         — five-gate ingress (input-type, audit, schema, branch, answer-class)
        ├── pipeline.ts       — laminar 1-4 / 5-8, triad 1-4 / 5-8 (4-call chain)
        ├── d9.ts             — Opus synthesis
        ├── oracle.ts         — Haiku canon-aware Q&A
        ├── engine2.ts        — legacy with dual-read fix applied
        ├── machines.ts       — registry + factory + CRUD
        └── health.ts         — liveness + secret presence
```

Total: ~1,486 lines across 10 TypeScript files plus config.

For comparison: same code in MySanctumLive lived as ~560 lines inside a 2,482-line monolithic `src/index.ts`. The split here is for readability, not capability — every endpoint behaves identically.

---

## WHAT'S DIFFERENT FROM MYSANCTUM

| Item | MySanctum | Michronics |
|---|---|---|
| KV binding | `SANCTUM_KV` | `MICHRON_KV` |
| KV namespace ID | `ae4649...d4cf5` | `d43d10...765e3` |
| Custom domain | `api.mysanctum.app` | `api.michronics.com` |
| Worker name | `mysanctum-api` | `michronics-worker` |
| Cron triggers | 7 (sprite/morning/sleep/etc.) | 0 (none — maths is on-demand) |
| `[[routes]]` in toml | Missing → drift trap | Explicit → zero drift |
| Code split | 1 file, 2,482 lines | 9 files, ~1,213 lines |
| Deep Ruby / Pattern Weaver / Still Mirror | Present in registry | Removed |
| Face 8 dual-read | Sanctuary still has main version (no dual-read); Session 61 branch has it but never deployed | Default behaviour, day one |
| Operational bucket | KV key exists (Session 61 sync) but engine2 doesn't read it on deployed Worker | Read by Face 8 + engine2 from day one |

---

## LIFTED CONTENT

### From `MySanctumLive/tools/` (Session 61 branch versions)
- `physics_canon.md` (487 lines)
- `physics_operational.md` (48 lines, NEW)
- `1_chronomics_clean_core.md` (320 lines)
- `3_ratified_rag.md` (337 lines)
- `0_dev_architecture.md`, `2_seeding_physics.md`, `4_economy_physics.md`, `5_dev_extra_ratified.md`, `6_sprint_directives.md`
- `PIPELINE_API_SPEC.md`
- `batch_runner_v3.py`, `sanctum_engine.py`, `sanctum_ratifier.py`, `chisel_thesis_briefing.md`

### From `MySanctumLive/continuity/`
- `chisel-onboarding.md`, `chisel-session-51.md`
- `archive-session60-threshold-trail.md`
- `MACHINE_SCHEMATIC.md`
- `machine-faces-session49.txt`, `five-equations-2026-04-08.html`, `t51-minimality-proof-2026-04-08.txt`
- Recent handovers (Sessions 58, 59, 60 day 1, 60 day 2)
- Legacy science docs (`legacy/` subdirectory)

---

## REMAINING WORK (post-Phase 1)

**Phase 2** — engines.html lift to Michronics frontend with:
- Triad/Laminar tabs only
- Machine factory UI
- Layer 0 declaration block
- Question pinned top, D9 below

**Phase 3** — parallel verification (sanctuary keeps full duplicate, both serve maths in parallel)

**Phase 4** — flip dispatch in pod.html / batch_runner / mobile-engine to point at api.michronics.com

**Phase 5** — strip maths from sanctuary src/index.ts, delete maths-only KV keys from sanctuary

See `MICHRONICS_SITE_MAP.md` (in repo root or Frontier's audit deliverable) for the full migration plan.

---

*Frontier audit pass · Phase 1 build · 27 April 2026*
