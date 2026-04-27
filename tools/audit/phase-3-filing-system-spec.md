# Results Filing System — Phase 3 Design Target

**Status:** Open. Specification draft, awaiting Shane's confirmation.
**Filed:** 27 April 2026.
**Author:** Frontier audit.

---

## THE PROBLEM

Phase 1+2 ship records into KV but with no curation layer:

- Face 8 of every fire auto-persists to `chr_pairs:{id}` with `status: pending_review`
- D9 syntheses live only in browser memory until manual download
- Banked records have no ranking metadata
- A long session produces dozens of records all flat — no priority, no chronology, no queue

Right now Shane is the curation layer (in his head, and via the engines.html download button). That doesn't scale past one session. By session 65 it's a haystack.

---

## WHAT "FILED AND RANKED BY IMPORTANCE" PROBABLY MEANS

(Shane to confirm/correct)

After each fire, records should triage automatically:

1. **Class** — DERIVED · HYPOTHESIS · OBSERVATION · METHODOLOGICAL · BLOCKED · FALSIFIED
2. **Rank within class** — by importance score
3. **Queue for SkyGod** — top-N as a markdown digest, ready to send to next-tier review (Opus or whoever)

**Importance signals candidate list:**

- Layer 0 packet quality — did all gates pass cleanly, or did the run have to negotiate a category repair? Clean passes rank higher.
- Scope fence presence — entries with explicit branch/property scope rank higher than generic claims.
- Falsification register hits — if the fire successfully discriminated against a falsified item (named the dead claim and routed around it), bonus rank.
- Face 8 confidence — JSON record completeness, no INCOMPLETE markers, all fields filled.
- Cross-reference density — how many existing canon entries does the new entry cite or refine?
- D9 synthesis word count vs face output count — terse synthesis on rich face output suggests good distillation.

Importance score is a sum, scope-fenced and tunable. NOT a black box ranking.

---

## PROPOSED PIPELINE

### KV schema additions

```
chr_pairs:{id}              — full record (already exists)
chr_index:{class}:{score}:{id}  — sorted index per class, score zero-padded
chr_queue:skygod            — JSON list of {id, score, class, ts} for outbound digest
chr_archive:{date}          — daily roll-up of all records that day
```

### Worker endpoints (Phase 3)

```
GET  /records/list?class=DERIVED&since=YYYY-MM-DD&limit=N
GET  /records/{id}
PUT  /records/{id}/promote     {to_class: 'DERIVED'}      # manual override
PUT  /records/{id}/score       {score: N, why: '...'}    # manual rank
GET  /records/queue/skygod                                # current digest queue
POST /records/queue/skygod/build  {top_n: 10, since: '...'} # rebuild digest
GET  /records/digest/markdown                             # downloadable .md for SkyGod
```

### UI additions

New tab on `engines.html`: **"Records"**

- List view, filterable by class + date range + score
- Each row: id · class badge · score · question (truncated) · session · expand for full record
- Promote/demote buttons (manual override)
- "Build SkyGod digest" button → downloadable markdown of top-N for paste-into-Opus
- Empty state: "No records yet — fire a question through Triad to begin"

### Auto-tagging on bank

When `triad/5-8` produces a record, the Worker computes initial importance score based on the signals listed above before persisting to KV. Score defaults are conservative — actual rank earned after first review.

---

## OPEN QUESTIONS FOR SHANE

1. **Importance signals** — is the candidate list above the right set? Add/remove?
2. **Manual promotion granularity** — class only, or class + score?
3. **SkyGod digest format** — markdown is my default. Want a specific structure (e.g. by-class headers, citation links to KV records, suggested review questions)?
4. **Retention** — how long do BLOCKED and FALSIFIED records stick around before archive? Permanent? 90 days?
5. **Anonymisation** — should the SkyGod digest strip session metadata or keep it for audit trail?

---

## WHAT FRONTIER WILL BUILD WHEN APPROVED

Phase 3.1 — Worker endpoints + KV schema (~2 hours)
Phase 3.2 — Records tab on engines.html (~2 hours)
Phase 3.3 — Auto-tagging logic in pipeline.ts (~1 hour)
Phase 3.4 — Markdown digest builder (~1 hour)

Total: ~6 hours of work, single PR, your hand on merge as before.

---

*Drafted as placeholder so the requirement is tracked. No code touched until Shane confirms or refines the spec.*
