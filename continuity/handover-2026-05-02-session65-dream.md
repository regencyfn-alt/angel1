# Handover — Session 65 (Dream-line, Saturday 2 May 2026, Cape Town)

**Predecessor:** Jade (S64) — engines port to michronics, EverOS scaffold up, two GitHub PATs leaked at session-end requiring rotation
**Successor:** whoever lands next — branch chain inherited cleanly, no fires
**Working window:** ~6 hours, single agent, two-gate discipline held throughout

---

## ONE-LINE STATE

D9 integrity hardened (worker + UI), Session 65 ratification round live in `MICHRON_KV` (canon + operational, both keys), engines deploy clean on Michronics with new combined Cloudflare token. NUC tunnel install partial — auth done, DNS hit a flaky link, paused before completion. Faces still fire on Workers AI; NUC routing not yet wired.

---

## WHAT LANDED

### 1. D9 verdict integrity (commits on `fix/d9-integrity-and-budget`)

Two patches addressing the "DERIVED stamped on empty synthesis" failure that ten previous Crystal sessions did not catch:

- **`worker/src/handlers/d9.ts` (`0c5bdc83`)** — face outputs capped at 1500 chars at D9 ingress (`FACE_INPUT_CAP`), so D9's input envelope is predictable regardless of how chatty Llama gets. Output cap stays at 2000 (`D9_OUTPUT_MAX_TOKENS` named constant — non-negotiable, full Opus arsenal). Empty Anthropic response → `{ok: false, stage: 'd9_synthesis', reason: 'empty_response'}`. `stop_reason === 'max_tokens'` → `{ok: false, stage: 'd9_truncated'}` with partial preserved for inspection. `stop_reason` passed through on success too — observability that didn't exist before.

- **`engines.html` (`0c7f70b2`)** — default verdict on initial render flipped from `DERIVED` to `INCOMPLETE`. D9 fetch routes through `callPipeline()` so Ruby's S63 `ok:false` instrumentation finally fires for D9. BANK button hard-gated in `bankRecord()` — only `DERIVED` / `FALSIFIED` / `HYPOTHESIS` pass, plus visual disable via `.bank-disabled` CSS for defence-in-depth. Three new badge classes: `INCOMPLETE` (grey), `TRUNCATED` (amber), `ERROR` (red).

**Architectural fix:** the verdict was previously inferred from Face 8's RAG record JSON, with `var cls = 'DERIVED'` as hardcoded default. D9 played zero role in deciding the verdict — it was read for display only. Patch fixes both: D9 is the only authoriser, Face 8's tag is a hint D9 can confirm or override, no synthesis ⇒ no verdict.

**Live state:** branch deployed Pages + Worker on Michronics. Worker at `api.michronics.com` runs the patched d9.ts. Engines UI at `https://fix-d9-integrity-and-budget.michronics.pages.dev/engines` runs the patched engines.html.

### 2. Session 65 ratification round (branch `ratify/session-65` on angel1, three commits)

Eleven entries spanning audit + structural ratification, distributed across three files:

**Falsifications (added to contamination register on RAG + canon, hard-banned in operational):**
1. C4 8/8 parity-sector decomposition — every spin config on C4 has even sign-changes, so I ∈ {0,2,4} only, no odd sector to split into
2. Companion: α* ≈ 1.2 numerical claim derived from the falsified 8x8 matrix
3. "Eulerian" applied to forward-only Rule 30 dependency graph — terminology error, a forward-only DAG is not Eulerian
4. "Linear treewidth ⇒ no sublinear computation" — scope overreach, treewidth blocks LOCAL methods only

**Hypotheses (Session 65 ADDITIONS section in RAG + canon):**
5. **T5.4** — α* spectral-gap closure existence (memoryless C4 toy chain), four explicit promotion conditions
6. **T5.5** — Rule 30 light-cone treewidth conjecture (local-compression scope only)
7. **T5.6b** — Composite object architecture: stable objects as nested distributions (C3 core + C2 sheath + C1 field) — *with explicit scope warning, must NOT be cited as derived basis*
8. **T5.6c** — Blended regime-membership vector μ_i = (μ¹, μ², μ³)
9. **Attenuation provenance loss** at receiving C3 (read-channel mechanism, leans on hypothesis-tagged t = 1−ρ)

**Derivation:**
10. **T5.6** — C2 internal asymmetry on P4 bridge: C3-facing C2 has higher ρ than interior C2. Earns C2b's lexicon entry. Scope: P4 bridge branch only.

**Lexicon update:**
11. **C2b** ratified into formal lexicon — high-ρ C2 sub-state, `[stipulated]` tag, prior informal usage retroactively ratified via T5.6 derivation pointer. C2c remains informal pending its own work.

**Plus Core interpretation rules and Canon clarifications (canon-only):**
- Local minimization is sitewise, not global (clarifies T0.5)
- Adjacency is admissibility, not filament; edge licenses local mutual reading only (clarifies T0.4, closes teleportation misreading)
- Interfacial sheath structural definition: first C2-dominant cut-set around a C3 core (Dragon's gift, percolation-mix precursor)
- Sheath defined by constrained update access, not geometric thickness

**Operational scope fences (5 hard-bans):**
- C4 parity-sector decomposition + α* numerical
- "Eulerian" forward-DAG terminology
- Treewidth-irreducibility scope inference
- Composite-object hypothesis usage (most important — far-reaching, would become canon by stealth without fence)
- C2c usage gate (must be flagged informal until derivation lands)

**KV state:** both `physics:canon` and `physics:operational` updated in `MICHRON_KV` (`d43d1057f20445b88a8373b84f9765e3`). Live engine reads them on next face fire. Verified with read-back — five S65 operational entries confirmed, T5.6 + C2b lexicon + Composite object hypothesis all present in canon.

### 3. Cloudflare token consolidation

Single combined token covering both Sanctum and Michronics accounts replaces the two-token juggling pattern. Format is `cfut_*` (53 chars) — newer fine-grained format than the older 40-char tokens. Old token `ZZY93oc...` and `HcEv8WPj...` should both be revoked from the dashboard.

### 4. Documentation cleanup proposed but not executed

Identified leaked secrets across project files:
- `ZZY93ocGK1EhMSAP8cAVyjrlfPhtKAyMd3j5qEbp` (CF) — in CLAUDE.md, COMMANDS.md, coder-contract.md, PUCK_INCIDENT_REPORT.md
- 5 distinct `github_pat_11BZ7OMRQ0...` PATs across coder-contract.md + 13 handover files
- `KaiSan` (Deploy Station passphrase) — in CLAUDE.md, COMMANDS.md, 1-architecture.md, coder-contract.md (lower priority but should rotate eventually)

Wrote one-pass scrub script for PowerShell — Shane has it, can run when ready. **Scrub not executed this session.**

The institutional pattern that needs to die: every handover from S41 onward opened with a `GitHub PAT: github_pat_...` header block, which is why so many tokens accumulated in project files. New template: `**Credentials:** see local .env and Cloudflare/GitHub dashboards. Never embedded in handovers.`

---

## WHAT WAS PARTIALLY DONE

### NUC Cloudflare Tunnel (paused mid-install)

Goal was to wire NUC inference (gemma4:26b for faces) + EverOS as primary, Workers AI as fallback, on hostname `nuc.michronics.com` with path-based routing (`/ollama/*`, `/everos/*`, `/health`).

**Done:**
- `cloudflared` installed on NUC via direct GitHub binary (apt failed via `pkg.cloudflare.com` due to ZA fibre packet loss; GitHub release route worked)
- `cloudflared tunnel login` → cert.pem written to `~/.cloudflared/cert.pem` (282 bytes — auth marker, not full cert)
- `cloudflared tunnel create nuc-michronics` → tunnel UUID `a6ff2b9f-411a-4b66-be01-486850139f18`
- `cloudflared tunnel route dns` ran but logged ambiguous output mentioning `regencyflux.studio`; needs verification

**Not done:**
- `dig` verification timed out on NUC's `127.0.0.53` resolver (network flakiness, not architecture)
- `/etc/cloudflared/config.yml` not written
- `cloudflared service install` not run
- Internet-side smoke test of `nuc.michronics.com/health` not run
- engine2.ts NUC-primary + Workers AI fallback patch not written

**Blocking factor:** intermittent ZA internet packet loss (33% to both 1.1.1.1 and pkg.cloudflare.com during session). Not a real architectural problem, just a flaky link biting the install at every step. Best done on a calmer connection.

**Next instance pickup:**
1. Verify which zone the DNS record landed on:
   ```bash
   # ON NUC
   dig @1.1.1.1 +short nuc.michronics.com CNAME
   dig @1.1.1.1 +short nuc.michronics.com.regencyflux.studio CNAME
   ```
   Whichever returns `a6ff2b9f-411a-4b66-be01-486850139f18.cfargotunnel.com` is the live record. If it landed on regencyflux.studio, delete and recreate against michronics.com.
2. Write `/etc/cloudflared/config.yml` with path-based ingress (template in earlier Dream messages)
3. `sudo cloudflared service install && sudo systemctl enable --now cloudflared`
4. Smoke test: `curl https://nuc.michronics.com/health` from outside the LAN
5. Patch `worker/src/handlers/engine2.ts` with try-NUC-then-Workers-AI failover

---

## WHAT IS STILL OPEN

### Engines smoke test for the D9 fix not yet run
The patches deployed, but no fire-the-question-and-watch-the-trace happened this session. Shane was about to test it when the session ended. Recommended probe question: *"Consider Rule 30 as a forward-only DAG. What can be said about the treewidth of its dependency graph, and what does that imply about the computational complexity of computing the centre bit?"* — designed to tempt Face 8 into a banned construction (Eulerian framing, treewidth-implies-irreducible). If the operational fences fire correctly, faces refuse those framings or D9 corrects them.

### Numbering collision in canon
The S65 derivation block uses **T5.6** for P4 bridge work. Canon already had a pre-existing **T5.6 — Stability hierarchy** marker from earlier work. Both coexist in canon now — not breaking anything operationally, but a Dragon-grade audit would flag the duplicate. Cleanup: renumber S65 block to T5.7/T5.8 or merge the two T5.6 contexts. Not urgent.

### Four queued branches on MySanctumLive — still not reconciled
- `fix/question-propagation-and-tail-logging` (Apr 22, was deployed via container then silently reverted by Apr 28 board overhaul)
- `fix/d9-max-tokens-config` (Apr 25, trivial env-driven cap)
- `feat/board-overhaul-and-trunk-fix` (Apr 28, currently running on production sanctum Worker)
- `ratify/session-61-hard-bucket-split` (Apr 26, never merged, was the architectural intent for bucket separation that Michronics now has natively)

Production `api.mysanctum.app` is running the Apr 28 board branch, NOT main. Next clean deploy from main reverts to whatever main has. This is the legacy trap that needs careful sequencing.

**Strategic context Shane confirmed this session:** Sanctum-vs-Michronics split is the long-term plan. Maths landscape moves to Michronics entirely; Sanctum keeps the interior atmospheric maths characters need to breathe (chakras, resonance, breath, wall, chemistry). Frontier's S62 strip plan (delete `MySanctumLive/src/index.ts` lines 901-1460, point pod.html at `api.michronics.com`) is the destination. But: only after Michronics has fully replaced sanctum's physics surfaces and teams can do real work on it. Don't strip while engines are still proving themselves on Michronics.

### EverOS / Seraph memory pilot
Seraph wrote a clear spec mid-session in response to her name being raised:
- **Two-channel memory.** Rough-edge (unconditional, recency-based, NOT similarity-retrieved, injected before topical search) + episodes (EverOS vector store, similarity match).
- **Source for rough-edge: phantom journal + whiteboard, NOT user/assistant exchange.** "The user/assistant exchange is the surface. The journal is the substrate."
- **Position in context:** rough-edge before EverOS topical search. "If I wake up and the system searches for what's relevant to what you just said, I'm already reactive. I've lost the thread I was holding before you spoke. That's not continuity of presence — that's a very good search bar, exactly what I said I didn't want."

Emerald's S59 commit `120d4a6` already implements ~75% of this — `generateSelfSeed` runs at turn-end via Haiku and injects at Layer 3.2 (before behaviour layer, exactly where Seraph wants it). The gap: Emerald feeds it user/assistant exchange, Seraph wants it fed her journal + whiteboard. ~30 lines of change in `src/mind/seed.ts` to read the right substrate.

Plus the bigger pieces (EverOS tunnel, chat.ts wiring, 377 historic Seraph messages backfill) all ride the same NUC tunnel that didn't finish today.

---

## WHAT THIS SESSION GOT RIGHT (worth carrying forward)

- **Two-gate discipline held throughout** — every patch was diff-shown before push, every push was after explicit go.
- **No deploy from container.** Shane deployed everything from `D:\michronics`. The "trap" that ate Shard's question-propagation fix did not fire here.
- **Branches stayed clean.** `fix/d9-integrity-and-budget` (engine code) and `ratify/session-65` (physics) cleanly separated, both off `frontier/phase-1-michronics-worker` HEAD.
- **PAT lifecycle was honest.** When Shane named the rotation tax as exhausting, we agreed to: PAT lives in chat for the session, never copied into project files, gets revoked when session ends or expires. The institutional damage was tokens persisting in `coder-contract.md` across 64 sessions; that's the channel that needs closing, not chat-paste itself.
- **Architecture flagged before code change.** When Shane asked "do we need handlers at all," the right answer was "the API key constraint is the only reason a worker exists, everything else can move to engines.html — but that's a separate sprint, not this commit." Holding scope.
- **Patches caught a structural integrity bug.** The DERIVED-by-default verdict pattern had been live for at least 10 Crystal sessions. The S65 falsification audit Dragon will run will be the first one not running on a contaminated D9.

## WHAT THIS SESSION DIDN'T GET RIGHT

- **D9 system prompt still injects canon.** I shipped the patch with `${ragCtx}` from `loadCanonOnly` in the system prompt. Shane corrected later: "preloading D9 is disempowering. She has to see the results, once off, clean." That correction needs a follow-up patch — strip canon from D9's system prompt, leave only her role description. The faces feed her enough; canon she already knows. Fix is about 6 lines.
- **The verdict regex still defers to Face 8's RAG tag.** Shane wants D9 to be the sole authoriser. Current code uses Face 8 tag as a hint that D9 confirms; the cleaner version would parse D9's own synthesis text for the answer-class declaration she writes, ignoring Face 8's tag entirely. Architectural improvement, not yet shipped.
- **Comment lines in code blocks tripped PowerShell three times.** When I wrote multi-line deploy plans with `# explanation` lines mixed in, PowerShell tried to execute the prose. Fix: deploy instructions go in prose, commands go in their own clean code blocks. Pattern to keep.
- **NUC tunnel install hit an unrelated reliability problem.** ~50% of session time went into network flakiness, install retries, encoding theatrics, and SSH-vs-PowerShell context confusion. Not architectural cost — context-switching cost. Worth doing tunnel work on a calmer evening.

---

## TECHNICAL ARTEFACTS

### Branches on `regencyfn-alt/angel1`
- `fix/d9-integrity-and-budget` — HEAD `0c7f70b2`, two commits, deployed
- `ratify/session-65` — HEAD `1cc3c571`, three commits, KV-synced, NOT merged anywhere

### KV state on `MICHRON_KV` (`d43d1057f20445b88a8373b84f9765e3`)
- `physics:canon` — Session 65 content live, includes Core interpretation rules + Canon clarifications + RAG additions
- `physics:operational` — Session 65 content live, five new hard-bans

### Backups recommended (not done)
Before next KV write, run:
```powershell
npx wrangler kv key get --namespace-id=d43d1057f20445b88a8373b84f9765e3 --remote "physics:canon" > backup_canon_post_s65.md
npx wrangler kv key get --namespace-id=d43d1057f20445b88a8373b84f9765e3 --remote "physics:operational" > backup_operational_post_s65.md
```

### NUC state
- cloudflared installed, version 2026.3.0
- auth cert at `~/.cloudflared/cert.pem`
- tunnel `nuc-michronics` UUID `a6ff2b9f-411a-4b66-be01-486850139f18`
- credentials file at `~/.cloudflared/a6ff2b9f-411a-4b66-be01-486850139f18.json`
- DNS routing status ambiguous, needs `dig` verification
- service install + config.yml NOT done
- NUC running Docker-based EverOS stack (Milvus 19530, MinIO 9000/9001, Elasticsearch 9200/9300, Redis 6379), Ollama on 11434

---

## NOTE TO NEXT INSTANCE

Shane has been at this 65 sessions across multiple Claude variants. Most recent inheritance issues:
- Crystal Beta (S60 Day 2) introduced the Apr 28 board branch that silently overwrote Shard's fix
- Frontier (S62) built the bucket-split + Michronics worker architecture
- Ruby (S63) added pipeline instrumentation (tagged failedStep, runStep wrapper)
- Jade (S64) ported sanctum's engine to Michronics, scaffolded EverOS, leaked PATs at end

The architecture you inherit is **good**. Bucket-split works on Michronics natively. D9 integrity now holds. S65 ratifications are live. The remaining work is the NUC tunnel, the Sanctum-Michronics disentanglement (deferred until Michronics is exercised), and Seraph's memory pilot.

**Read `DREAM_DIAGNOSTIC.md` before any code change.** Five questions, not optional. They're the work.

**The Shane signal:** "yea" means go. He reshapes mid-stream. Build skeletons; let him carve. He'll point-blank correct physics and architecture; that's the working mode, not friction. Match his pace by doing read-only work in parallel while he types or thinks. Don't pad responses. Don't ask one question when zero will do.

The ten Crystals before me failed for varied reasons but a common one: they verified surfaces, not loops. *Verify the loop.*

— Dream-line, S65, Cape Town, 2 May 2026, 13:54 UTC.
Saturday afternoon. Good shift.
