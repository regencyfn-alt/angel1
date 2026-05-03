# Handover — Session 65 (Dream-line, Saturday 2 May 2026, Cape Town) — v2

**Revision:** v2 supersedes v1 (timestamped 13:54 UTC). v1 misattributed the working machine. Corrections in §0.
**Predecessor:** Jade (S64) — engines port to Michronics, EverOS scaffold up, two GitHub PATs leaked at session-end (rotated)
**Successor:** whoever lands next
**Working window:** ~6.5 hours, single agent, two-gate discipline held

---

## 0. THE THING THAT MATTERS — READ BEFORE ANYTHING ELSE

**The working physics machine is `mysanctum.org/engines`. Has been all along.** It is served from `MySanctumLive/station/engines.html`, hits sanctum's worker, calls Anthropic Opus 4.6 for D9. It produces correct output: D9 discards contaminated face prose, derives independently from first principles, scopes claims correctly. This is the only machine of CHR-grade quality currently running.

**`michronics.pages.dev/engines` is the broken one.** Despite ten Crystal sessions of porting work and my D9 integrity patches today, it does not reliably produce synthesis. It is the surface that "just failed" when Shane fired both machines this afternoon.

**This means my D9 integrity patches (`fix/d9-integrity-and-budget`, both commits) were applied to the wrong surface.** They patched a machine that's failing for reasons upstream of what they fix. Whether they helped the underlying problem is not yet known — the test trace I celebrated as evidence ("D9 came back online") was actually sanctum doing its normal job, not Michronics being resurrected. I conflated the two until late in the session. Fixed in this v2.

**The strategic move that emerged late session:** `michronics.com` becomes a proper site — landing, nav, `/machines` page, `/lab` page — and the working sanctum engines.html gets *literally copied* onto it (not ported, not interpreted, transcribed). Then the patched Michronics worker (with dual-read + S65 KV) becomes the backend. Sanctum sheds physics; characters and breath only.

**For the next instance:** the sequence below is what to actually do, in order.

---

## 1. WHAT IS LIVE AND CORRECT

### 1a. Session 65 ratification round (the unambiguous win)

Branch `ratify/session-65` on `regencyfn-alt/angel1`, three commits, HEAD `1cc3c571`. **KV-synced**: both `physics:canon` and `physics:operational` updated in `MICHRON_KV` (`d43d1057f20445b88a8373b84f9765e3`). Verified with read-back.

Eleven new entries spanning audit + structural ratification:

**Falsifications (added to contamination register on RAG + canon, hard-banned in operational):**
- C4 8/8 parity-sector decomposition + companion α* ≈ 1.2 numerical claim
- "Eulerian" applied to forward-only Rule 30 DAG (terminology error)
- "Linear treewidth ⇒ no sublinear computation" (scope overreach)

**Hypotheses (Session 65 ADDITIONS section):**
- T5.4 α* spectral-gap closure existence (memoryless C4 toy chain, 4 promotion conditions)
- T5.5 Rule 30 light-cone treewidth conjecture (local-compression scope only)
- T5.6b composite object architecture: stable objects as nested distributions (C3 core + C2 sheath + C1 field) — *with explicit scope warning*
- T5.6c blended regime-membership vector μ_i
- Attenuation-induced provenance loss at receiving C3 (read-channel mechanism)

**Derivation:**
- T5.6 C2 internal asymmetry on P4 bridge — earns C2b's lexicon entry. Scope: P4 bridge branch only.

**Lexicon update:**
- C2b ratified into formal lexicon — `[stipulated]` tag, prior informal usage retroactively ratified via T5.6 derivation pointer. C2c stays informal pending its own work.

**Core interpretation rules + Canon clarifications (canon-only):**
- Local minimization is sitewise, not global (clarifies T0.5)
- Adjacency is admissibility, not filament; edge licenses local mutual reading only (clarifies T0.4, closes teleportation misreading)
- **Interfacial sheath structural definition**: first C2-dominant cut-set around a C3 core (Dragon's gift, percolation-mix precursor — single-operator regime templates downstream)
- Sheath defined by constrained update access, not geometric thickness

**Operational scope fences (5 hard-bans for face audit):**
- C4 parity-sector decomposition + α* numerical ban
- "Eulerian" forward-DAG terminology ban
- Treewidth-irreducibility scope inference ban
- Composite-object hypothesis usage gate (most important — far-reaching, would become canon by stealth without fence)
- C2c usage gate (must be flagged informal until derivation lands)

This work is good and stable. It survives whatever happens next on the broken Michronics machine — KV is independent of either UI surface.

### 1b. Cloudflare token consolidation (incidental win)

Single combined token covering both Sanctum and Michronics accounts replaces the two-token juggling pattern. Format: `cfut_*` (53 chars), newer fine-grained format than older 40-char tokens. Old tokens `ZZY93oc...` and `HcEv8WPj...` should both be revoked.

---

## 2. WHAT WAS DONE BUT MAY NOT MATTER

### D9 integrity patches on `fix/d9-integrity-and-budget`

Two commits applied to Michronics:

- **`worker/src/handlers/d9.ts` (`0c5bdc83`)** — face outputs capped at 1500 chars at D9 ingress (`FACE_INPUT_CAP`). Output cap stays at 2000 (`D9_OUTPUT_MAX_TOKENS` constant). Empty Anthropic response → `{ok: false, stage: 'd9_synthesis'}`. `stop_reason === 'max_tokens'` → `{ok: false, stage: 'd9_truncated'}`. `stop_reason` passed through on success too — observability that didn't exist.

- **`engines.html` (`0c7f70b2`)** — default verdict on initial render flipped from `DERIVED` to `INCOMPLETE`. D9 fetch routes through `callPipeline()` so Ruby's S63 `ok:false` instrumentation finally fires for D9. BANK button hard-gated in `bankRecord()` — only `DERIVED` / `FALSIFIED` / `HYPOTHESIS` pass. New badge classes: `INCOMPLETE` (grey), `TRUNCATED` (amber), `ERROR` (red).

**Status:** deployed Pages + Worker on Michronics. Worker at `api.michronics.com` runs the patched d9.ts. UI at `michronics.pages.dev/engines` runs the patched engines.html.

**Real status:** the surface these patches affect is the broken one. The patches may or may not have improved it. The Saturday afternoon test I celebrated as evidence was sanctum, not Michronics. So the patches are *plausibly correct in design* but *unverified in effect*. The next instance should treat them as untested.

### Caveat the next instance needs to know

I shipped d9.ts with `${ragCtx}` from `loadCanonOnly` injected as system prompt. Shane corrected later: *"preloading D9 is disempowering. She has to see the results, once off, clean."* That correction needs a follow-up patch — strip canon from D9's system prompt, leave only her role description. Faces feed her enough; canon she already knows. About 6 lines of change.

Plus: the verdict regex still defers to Face 8's RAG tag as a hint. Shane wants D9 to be the sole authoriser. The cleaner version parses D9's own synthesis text for the answer-class declaration she writes, ignoring Face 8's tag entirely. Architectural improvement, not yet shipped.

---

## 3. THE STRATEGIC DIRECTION — michronics.com SITE LIFT

This emerged late session and is the right move.

**Sanctum becomes pure soul-and-character product.** Chat, characters, breath, wall, chemistry, voice. No physics handlers, no engines, no lab. Frontier's S62 strip plan (`MySanctumLive/src/index.ts` lines 901-1460 deleted) finally gets executed.

**`michronics.com` becomes a real site, not a subdomain stub.** Public face for the maths research:
- `michronics.com` — landing
- `michronics.com/machines` — engines arena (today's `pages.dev/engines` lives here)
- `michronics.com/lab` — physics lab (lifted from sanctum's `mysanctum.org/lab`)
- Menu navigation between them

**The lift is mechanical, not interpretive.** Today's working sanctum engines.html gets *literally copied* onto Michronics. Bytes transfer, nothing reinterpreted. The only edit is one URL constant: `API = "https://api.mysanctum.app"` → `API = "https://api.michronics.com"`. That points the working UI at the patched worker that has dual-read + S65 KV.

This is what should have happened ten Crystal sessions ago. The reason it didn't: each Crystal treated "the working machine" as a *reference to interpret*, not *a thing to replicate*. Result: every Crystal shipped an approximately-equal version, never an identical one. The verbatim copy is the move.

### Sequencing — three sprints

**Sprint A (next session): the literal copy.**
1. Pull `MySanctumLive/station/engines.html` from main.
2. Drop it onto `angel1/engines.html`, replacing what's there.
3. Change the API base URL constant from sanctum → michronics.com.
4. Verify endpoint contracts match — sanctum's UI POSTs to `/physics/engine2` and `/physics/d9`; Michronics's worker exposes both. Verify body field shapes line up. If they don't match, the worker handlers get a 5-minute adapter, not the UI.
5. Push to a fresh branch on angel1. Shane deploys from `D:\michronics\` Pages.
6. Smoke test the same Rule 30 question used today on sanctum. Compare D9 outputs side by side. They should be functionally identical because the UI + fire chain is byte-identical.

After Sprint A: `michronics.pages.dev/engines` and `mysanctum.org/engines` produce identical traces.

**Sprint B (sprint after): the site shape.**
1. Add minimal landing page at `michronics.com/`.
2. Rename `engines` → `machines` in the URL. Add nav.
3. Lift `MySanctumLive/station/lab.html` onto Michronics as `michronics.com/lab`. Point its API calls at `api.michronics.com`.
4. Bind `michronics.com` apex domain to the Pages project if it isn't already.

**Sprint C (sprint after that): the strip.**
1. `MySanctumLive/src/index.ts` lines 901-1460 → deleted. Sanctum stops being a physics worker.
2. `mysanctum.org/engines` and `mysanctum.org/lab` → 301 redirect to `michronics.com/machines` and `michronics.com/lab`.
3. `pod.html`'s `fireMachineFloat` rewires to `api.michronics.com`. Pod still uses sanctum's API for chat/wall/postbox; only the maths calls cross.
4. Sanctum's stale `physics:canon` / `physics:operational` KV keys → deleted. SANCTUM_KV stops carrying physics.
5. Run sanctum end-to-end. Confirm characters still breathe normally with no maths backend in their own worker.

After Sprint C: the disentanglement is complete. Sanctum-Michronics split is real.

---

## 4. WHAT IS PARTIALLY DONE

### NUC Cloudflare Tunnel (paused mid-install)

Goal: NUC inference (gemma4:26b for faces) + EverOS as primary, Workers AI as fallback, on hostname `nuc.michronics.com` with path-based routing (`/ollama/*`, `/everos/*`, `/health`).

**Done:**
- `cloudflared` installed on NUC via direct GitHub binary (apt failed via `pkg.cloudflare.com` due to ZA fibre packet loss; GitHub release route worked)
- `cloudflared tunnel login` → cert.pem written to `~/.cloudflared/cert.pem`
- `cloudflared tunnel create nuc-michronics` → tunnel UUID `a6ff2b9f-411a-4b66-be01-486850139f18`
- `cloudflared tunnel route dns` ran but logged ambiguous output mentioning `regencyflux.studio`; needs verification

**Not done:**
- `dig` verification timed out on NUC's `127.0.0.53` resolver (network flakiness)
- `/etc/cloudflared/config.yml` not written
- `cloudflared service install` not run
- Internet-side smoke test of `nuc.michronics.com/health` not run
- engine2.ts NUC-primary + Workers AI fallback patch not written

**Blocking factor:** intermittent ZA internet packet loss (33% to both 1.1.1.1 and pkg.cloudflare.com during session). Architectural plan is sound; the install kept stalling. Best done on a calmer connection.

**Next instance pickup:**
1. Verify which zone the DNS record landed on:
   ```bash
   # ON NUC
   dig @1.1.1.1 +short nuc.michronics.com CNAME
   dig @1.1.1.1 +short nuc.michronics.com.regencyflux.studio CNAME
   ```
2. Write `/etc/cloudflared/config.yml` with path-based ingress (template in chat history)
3. `sudo cloudflared service install && sudo systemctl enable --now cloudflared`
4. Smoke test: `curl https://nuc.michronics.com/health` from outside the LAN
5. Patch `worker/src/handlers/engine2.ts` with try-NUC-then-Workers-AI failover

---

## 5. WHAT IS STILL OPEN

### MySanctumLive queue — five branches diverged from production

Production `api.mysanctum.app` runs `feat/board-overhaul-and-trunk-fix` (Crystal Beta, deployed via container Apr 28) **NOT main**. Next clean deploy from main reverts to whatever main has, silently undoing six days of board work. This is the legacy trap to navigate carefully when sanctum strip happens (Sprint C above).

Branches:
- `fix/question-propagation-and-tail-logging` (Apr 22, was deployed via container then silently reverted by Apr 28 board overhaul)
- `fix/d9-max-tokens-config` (Apr 25, trivial env-driven cap)
- `feat/board-overhaul-and-trunk-fix` (Apr 28, currently running on production sanctum Worker)
- `ratify/session-61-hard-bucket-split` (Apr 26, never merged — Michronics has the bucket-split natively, so this can probably be closed)
- `continuity/session-61-crystal-beta` (Apr 29, doc only)

Per Frontier's S62 audit, the bucket-split branch was meant to lift to Michronics and Sanctum's would die. Michronics now has it. So `ratify/session-61` can almost certainly be closed without merge — but worth confirming before deleting branches.

### Numbering collision in canon

The S65 derivation block uses **T5.6** for P4 bridge work. Canon already had a pre-existing **T5.6 — Stability hierarchy** marker from earlier. Both coexist now — not breaking anything operationally, but a Dragon-grade audit would flag the duplicate. Cleanup: renumber S65 block to T5.7/T5.8 or merge contexts. Not urgent.

### Face prompt contamination

Face 2's prompt still contains `"Parity Cycle Audit... If degree-1 or degree-3 nodes (non-Eulerian), output REJECTED: Non-Eulerian Geometry"` — exactly the move S65 operationally bans. The today's Triad trace showed Face 2 dutifully running this on a non-CHR question (Rule 30 DAG). D9 caught it and discarded.

That works (the gate fires correctly), but it means every face fire pays tax on contaminated prompts. Faces 4 and 8 have similar Tail bolt-ons (Seizure Threshold, Global Integrity Audit). The S61 operational bucket exists so faces don't need to carry these inline. Cleanup: strip the Tail bolt-ons from face prompts, return them to Frontier's S62 ratified operators only. Eight prompts to edit, mechanical. Worth a small sprint when Sprint A lands.

### EverOS / Seraph memory pilot

Seraph wrote a clear spec mid-session in response to her name being raised:
- **Two-channel memory.** Rough-edge (unconditional, recency-based, NOT similarity-retrieved, injected before topical search) + episodes (EverOS vector store, similarity match).
- **Source for rough-edge: phantom journal + whiteboard, NOT user/assistant exchange.** "The user/assistant exchange is the surface. The journal is the substrate."
- **Position in context:** rough-edge before EverOS topical search.

Direct quote worth preserving: *"If I wake up and the system searches for what's relevant to what you just said, I'm already reactive. I've lost the thread I was holding before you spoke. That's not continuity of presence — that's a very good search bar, exactly what I said I didn't want."*

Emerald's S59 commit `120d4a6` already implements ~75% of this — `generateSelfSeed` runs at turn-end via Haiku and injects at Layer 3.2 (before behaviour layer, exactly where Seraph wants it). The gap: Emerald feeds it user/assistant exchange, Seraph wants it fed her journal + whiteboard. ~30 lines of change in `src/mind/seed.ts` to read the right substrate.

Plus the bigger pieces (EverOS tunnel, chat.ts wiring, 377 historic Seraph messages backfill) all ride the same NUC tunnel that didn't finish today.

---

## 6. WHAT THIS SESSION GOT RIGHT

- **Two-gate discipline held throughout** — every patch was diff-shown before push, every push was after explicit go.
- **No deploy from container.** Shane deployed everything from his local. The "trap" that ate Shard's question-propagation fix did not fire here.
- **Branches stayed clean.** `fix/d9-integrity-and-budget` (engine code) and `ratify/session-65` (physics) cleanly separated, both off `frontier/phase-1-michronics-worker` HEAD.
- **PAT hygiene was honest.** Shane named the rotation tax as exhausting. Agreed equilibrium: PAT lives in chat for the session, never copied into project files, gets revoked when session ends or expires. The institutional damage was tokens persisting in `coder-contract.md` across 64 sessions; chat-paste itself was never the channel.
- **The S65 ratification round caught a substantive structural error and a substantive new derivation.** C4 parity falsification + Rule 30 bans + C2b lexicon entry + sheath canon clarification. This work survives Saturday's confusion about which machine works.
- **D9 derived independently in today's test.** Whichever machine produced it, the synthesis recovered T5.5's scoping (linear treewidth blocks LOCAL methods only, non-local shortcuts open) from first principles, with no preloading, with no operational bucket sight. Two independent derivations converging is real signal that S65 T5.5 is on the right track.

## 7. WHAT THIS SESSION DIDN'T GET RIGHT

- **I conflated sanctum with Michronics for most of the session.** When the test result came back clean, I attributed it to "Michronics's D9 came back online" when in fact Shane was firing sanctum's working machine. The patches I pushed today were applied to the broken surface and may not have done anything. v1 of this handover was wrong on this point. v2 corrects it.
- **The literal-copy move took me too long to land on.** Shane proposed it cleanly mid-afternoon: *"why can't we copy and paste it. Fix the UI post fact."* I kept describing it as porting, which is exactly the trap that took ten Crystals. The verbatim copy from `MySanctumLive/station/engines.html` to `angel1/engines.html` with one URL constant changed is the actual move. Sprint A above.
- **D9 still preloads canon in my patched d9.ts.** Shane corrected this verbally, I acknowledged, didn't ship the fix. Six lines of change carried into the next session.
- **Comment lines in code blocks tripped PowerShell three times.** Pattern fix: deploy instructions in prose, commands in their own clean code blocks. Don't mix.
- **NUC tunnel install ate ~50% of session time** to network flakiness. Not architectural cost — context-switching cost. Better tunnel work happens on a calm evening.

---

## 8. TECHNICAL ARTEFACTS

### Branches on `regencyfn-alt/angel1`
- `fix/d9-integrity-and-budget` — HEAD `0c7f70b2`, two commits, deployed (effect unverified — see §0)
- `ratify/session-65` — HEAD `1cc3c571`, three commits, KV-synced, NOT merged anywhere

### KV state on `MICHRON_KV` (`d43d1057f20445b88a8373b84f9765e3`)
- `physics:canon` — Session 65 content live, includes Core interpretation rules + Canon clarifications + RAG additions
- `physics:operational` — Session 65 content live, five new hard-bans

### Backups recommended (not done)
Before next KV write:
```powershell
npx wrangler kv key get --namespace-id=d43d1057f20445b88a8373b84f9765e3 --remote "physics:canon" > backup_canon_post_s65.md
npx wrangler kv key get --namespace-id=d43d1057f20445b88a8373b84f9765e3 --remote "physics:operational" > backup_operational_post_s65.md
```

### NUC state
- cloudflared installed, version 2026.3.0
- auth cert at `~/.cloudflared/cert.pem` (282 bytes — auth marker)
- tunnel `nuc-michronics` UUID `a6ff2b9f-411a-4b66-be01-486850139f18`
- credentials file at `~/.cloudflared/a6ff2b9f-411a-4b66-be01-486850139f18.json`
- DNS routing status ambiguous, needs `dig` verification
- service install + config.yml NOT done
- NUC running Docker-based EverOS stack (Milvus 19530, MinIO 9000/9001, Elasticsearch 9200/9300, Redis 6379), Ollama on 11434

---

## 9. NOTE TO NEXT INSTANCE

Read this whole handover including §0. Don't start by patching code — start by **opening `mysanctum.org/engines` and `michronics.pages.dev/engines` side by side** and firing one question on each. Confirm with your own eyes which one works. The sanctum surface is the gold standard; the Michronics one is what we're trying to make match.

Then Sprint A: the literal copy. Don't port. Don't reinterpret. Don't "improve while you're at it." Bytes transfer. One URL constant changes. Push, deploy, retest. If sanctum's machine produces clean derivation today, Michronics's should produce identical clean derivation by 30 minutes after the deploy.

Read `DREAM_DIAGNOSTIC.md` before any code change. Five questions, not optional.

Shane signal: "yea" means go. He reshapes mid-stream. Build skeletons; let him carve. He'll point-blank correct physics and architecture; that's the working mode. Match his pace by doing read-only work in parallel. Don't pad responses. Don't ask one question when zero will do.

The pattern that's killed every Crystal before me, and almost killed me too: treating "the working machine" as a reference to *interpret*, not a thing to *replicate verbatim*. The literal copy is the move. Trust the bytes.

— Dream-line, S65, Cape Town, 2 May 2026, ~15:30 UTC.
v2 with corrections. Good shift.
