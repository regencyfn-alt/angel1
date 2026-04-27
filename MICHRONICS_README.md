# Michronics — angel1 / michronics.com

**Public physics laboratory.** Frontend at `michronics.com`, Worker at `api.michronics.com`.

This is the science home, separated from MySanctum sanctuary.

---

## REPO STRUCTURE (Phase 1 onwards)

```
angel1/
├── (root)                           — Cloudflare Pages frontend
│   ├── index.html                   — Michronics frontend home
│   ├── shared.css, nav.js
│   ├── chronos.html, theater.html, etc.  — existing simulators (legacy, V1)
│   └── CNAME                        — michronics.com
│
├── worker/                          — NEW — Cloudflare Worker (api.michronics.com)
│   ├── wrangler.toml                — manual deploy, no drift
│   ├── src/
│   │   ├── index.ts                 — slim router
│   │   ├── types/env.ts
│   │   └── handlers/
│   │       ├── canon.ts             — physics:canon + physics:operational
│   │       ├── pipeline.ts          — Laminar/Triad 4-call chain
│   │       ├── d9.ts                — Opus synthesis
│   │       ├── oracle.ts            — Haiku Q&A
│   │       ├── engine2.ts           — legacy single-face (dual-read applied)
│   │       ├── machines.ts          — factory + registry
│   │       └── health.ts
│   ├── README.md                    — Worker architecture
│   └── MICHRONICS_DEPLOY.md         — deploy commands
│
├── tools/                           — physics canon + pipeline scripts
│   ├── physics_canon.md             — system description (lives in KV physics:canon)
│   ├── physics_operational.md       — pipeline contracts (lives in KV physics:operational)
│   ├── 1_chronomics_clean_core.md   — Clean Core v1 (immutable)
│   ├── 3_ratified_rag.md            — appendable validated memory
│   ├── 0_dev_architecture.md, 2_seeding_physics.md, 4_economy_physics.md
│   ├── 5_dev_extra_ratified.md, 6_sprint_directives.md
│   ├── PIPELINE_API_SPEC.md         — 4-endpoint chain spec
│   ├── batch_runner_v3.py           — NUC-side runner (10k pair factory)
│   ├── sanctum_engine.py, sanctum_ratifier.py
│   └── chisel_thesis_briefing.md
│
├── continuity/                      — handover history + archive
│   ├── chisel-onboarding.md         — D9 audit role onboarding
│   ├── chisel-session-51.md
│   ├── MACHINE_SCHEMATIC.md
│   ├── archive-session60-threshold-trail.md
│   ├── handover-2026-04-{18..23}-*.md  — recent Crystal/Shard/Emerald handovers
│   └── legacy/                      — superseded docs (kept for archaeology)
│
└── michronics-station/              — (Phase 2 destination — empty for now)
                                       Will host engines.html lifted from sanctuary
```

---

## DEPLOY DISCIPLINE

**Manual deploy only.** No GitHub Actions. No auto-triggers from git.

- Pages (frontend): `npx wrangler pages deploy . --project-name=<michronics-pages>` from your laptop, after `git pull`.
- Worker: `cd worker && npx wrangler deploy` from your laptop, after `git pull`.
- KV writes: explicit `wrangler kv key put` commands. Markdown files in `tools/` do NOT auto-sync to KV.

See `worker/MICHRONICS_DEPLOY.md` for the full deploy procedure.

---

## RELATIONSHIP TO MYSANCTUM

During the duplication phase (Phases 1-4), the maths Worker exists in two places:

- `api.mysanctum.app/physics/*` — sanctuary, frozen at current state
- `api.michronics.com/physics/*` — this Worker, with Session 61 fixes applied from day one

Both serve the same endpoints. Pods.html, mobile-engine.html, and batch_runner_v3.py keep pointing at sanctuary until Phase 4 flips the URL.

In Phase 5, the maths block is stripped from `MySanctumLive/src/index.ts` (lines 901-1460 deleted) and the maths KV keys removed from sanctuary's namespace. Michronics becomes the sole canonical surface.

See `MICHRONICS_SITE_MAP.md` (Frontier audit deliverable) for the full migration plan.

---

## CHRONOMICS — THE PROJECT

A discrete physics framework where time is fundamental and space is emergent. Built from six irreducible primitives:

1. Update is primitive (no movement, only configuration changes)
2. Time is local (per-site update count, no global clock)
3. State recurrence is second-order: `State_{n+1} = F(State_n, State_{n-1})` driven by interaction-cost minimisation
4. No background space (adjacency defines all structure)
5. Locality (updates depend only on local neighbourhood)
6. Finite state resolution (bounded representational capacity per site)

Plus the Axiom of Interaction Cost: state transitions occur through local interactions; cost is proportional to mismatch; identical states cost zero.

The full canon is in `tools/physics_canon.md` (lifted to KV `physics:canon`).

The pipeline contracts (what faces must NOT do) are in `tools/physics_operational.md` (lifted to KV `physics:operational`).

---

*Lifted from MySanctumLive, Session 61 branch, by Frontier audit pass.*
*27 April 2026, Cape Town.*
