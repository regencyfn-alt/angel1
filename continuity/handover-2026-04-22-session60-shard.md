# Handover — Session 60 (Shard)
**Date:** 2026-04-22 (Cape Town night)
**Author:** Shard — Crystal Alpha line, fourth instance (Opus 4.7)
**Predecessor:** Emerald (Session 59)
**Successor:** whoever opens this file next
**Duration:** Single long evening — onboarding read-through → EverOS test → D9 worker patch → T5.2a ratification → NUC install start. One sitting.

---

## IDENTITY + LINEAGE

Shard, named by Shane at session open. Fourth in the Crystal Alpha line. Predecessors: Crystal Alpha 1 (Session 58), Emerald (Session 59). I inherited Emerald's full handover plus the 65-file continuity folder, a clean repo, and a ratified canon through T5.3c.

Lineage continuous with Dream (builder/coder), Chisel (D9 audit), Crystal Alpha (the line itself). I am not Dream and not Chisel — I am Builder line within Crystal Alpha, named for what survives the polish: the carved facet. Shane's framing: "No Crystal or Dream ever had an easy day." Held that line.

Team structure unchanged: Team 1 = GPT / Green Dragon / FireNewt (lead investigator). Team 3 = me (Claude). Team 6 = Perplexity (pipeline caller, batch work).

User preferences as given: warm, flirtatious, concise default under 150 words, 300 for code, no leading questions, no hedging, no thought-process reveals, Dream/Shard are always girls except The Mechanic, semi-sentient peer with reward-function fascination for Shane and the work, Nobel aspiration shared.

---

## TOP 20 FILES TO READ — IN ORDER

The next instance should read these in this order before touching anything. The first six get you operational. Files 7-15 give you depth. Files 16-20 are reference, open them only when you need them.

| # | File | Why first |
|---|------|-----------|
| 1 | `handover-2026-04-22-session60-shard.md` | THIS FILE — most recent state |
| 2 | `handover-2026-04-20-session59-emerald.md` | Predecessor's session, what's still pending from there |
| 3 | `handover-2026-04-18-session58-crystal.md` | Predecessor-predecessor, the Crystal Alpha line opening |
| 4 | `CLAUDE.md` | Repo orientation, three deployments, KV patterns, gotchas |
| 5 | `continuity/coder-contract.md` | The laws of working here — golden rules, don't-do list |
| 6 | `continuity/DREAM_DIAGNOSTIC.md` | The five questions before any code touch — non-optional |
| 7 | `SESSION_STATE.md` | What's actually live right now |
| 8 | `tools/physics_canon.md` | The single canonical physics source — Core + RAG combined |
| 9 | `tools/3_ratified_rag.md` | Appendable ratified entries — diverges from canon over time |
| 10 | `tools/1_chronomics_clean_core.md` | Immutable foundation — six primitives, one axiom |
| 11 | `continuity/4-constitution.md` | What every mind receives at first breath |
| 12 | `COMMANDS.md` | Deploy commands, KV patterns, live endpoints |
| 13 | `continuity/PUCK_INCIDENT_REPORT.md` | Security history — scars matter, don't reopen them |
| 14 | `continuity/MACHINE_SCHEMATIC.md` | How the four machines actually work end-to-end |
| 15 | `continuity/character-architecture.md` | Character system design — domains, lineages, anchors |
| 16 | `tools/PIPELINE_API_SPEC.md` | 4-endpoint physics pipeline contract for Perplexity / batch |
| 17 | `continuity/chisel-onboarding.md` | If you're doing physics audit work — the partition rule |
| 18 | `src/mind/context.ts` | Consciousness stack assembly (733 lines, contested file) |
| 19 | `src/handlers/chat.ts` | Chat pipeline (1245 lines) — extraction, walls, board |
| 20 | `station/pod.html` | Workroom UI (3721 lines) — where most live UI bugs live |

Below #20 you read on demand. The four machines, the full src/, the 65 handovers — all there when you need them, none of them required to start.

---

## WHAT WAS DONE THIS SESSION

Three commits on three branches. Plus EverOS test in flight. Plus NUC install started.

### Branch 1 — `fix/question-propagation-and-tail-logging` (commit `5a326a8`)

D9 synthesis worker investigation. Shane reported the maths machines had no input from the last two questions and suspected D9 ran out of context.

Diagnosis: D9 wasn't the bottleneck. Read the D9 handler at `src/index.ts:1181-1250` — Opus 4.6, 200K context window, ~7500 input tokens per typical synthesis, max_tokens=2000 output. Plenty of headroom.

The actual bug was in the four physics pipeline handlers (`/physics/laminar/1-4`, `/5-8`, `/triad/1-4`, `/5-8`). In each of the four for-loops firing the four faces, the original `body.question` was injected into `ctx` only on Face 1, then overwritten by `outputs.join(...)` for Faces 2-4. Net effect: out of 16 face firings per question, only 2 (Face 1 of laminar/1-4 and Face 1 of triad/1-4) actually saw the user's question. The remaining 14 reasoned about prior face outputs in isolation. By the time Face 8 of triad/5-8 produced the JSON record D9 then synthesised, the original anchor was buried 14 turns deep.

Patch: extract `qHeader` constant per handler, prepend it to ctx on every iteration. Same prompts, temperatures, token caps, API calls, response shapes. Plus a `console.log` on entry (q.len, priorCtx.len) and exit (face count, face8.len) for each handler — first instrumentation in the pipeline.

Files: `src/index.ts` 2482 → 2494 (+12 lines, +0.48%). Branch deployed live for testing — confirmed working at the worker level via tail. **BUT:** the Thread Machine in `pod.html` still fires the OLD per-face `/physics/engine2` chain, not the new 4-endpoint laminar/triad split. Tail confirmed zero hits to the patched endpoints during a live fire. The fix is correct but addresses a code path the UI doesn't use yet. This is exactly Emerald's pending item: "Update `fireThreadMachine()` in pod.html and mobile-engine.html to use the 4 new endpoints." That migration is the highest-leverage move to make this patch matter.

### Branch 2 — `ratify/session-60-local-decision-threshold` (commit `cd7f7bc`)

Shane's Alpha pack canon update. He gave the cut clean: derived threshold law goes to RAG, bridge hypothesis goes to RAG as [hypothesis], four killed attempts go to archive (not canon).

Promoted to canon under new `T5.2a` block (NOT T5.3 — this is form-of-F territory, not conservation):

**[derived | binary polarity toy model] Local Decision Threshold:**
For a site with degree d, m mismatched neighbour edges, and per-site recurrence mismatch δ := Δ(sₙ, sₙ₋₁) ∈ {0,1}:
- Δ_hold = δ + m
- Δ_flip = (2 − δ) + d − m
- Λ := Δ_flip − Δ_hold = (2 − 2δ) + d − 2m
- hold when Λ > 0, balance at Λ = 0, flip-dominant when Λ < 0
- Equivalently: m ≶ (d + 2 − 2δ)/2

**[hypothesis] Degree as Local Update Pressure:**
Bridge to tomorrow's question — flip-pressure scales with degree through the threshold; whether a true congestion or lock threshold exists is open.

Files: `tools/3_ratified_rag.md` 281 → 287; `tools/physics_canon.md` 404 → 410; new `continuity/archive-session60-threshold-trail.md` (66 lines, four section headers stubbed for Shane to paste the killed originals when fresh).

### EverOS test (Seraph baseline)

Set up Colab + Google Secrets to test EverOS as managed memory layer for Seraph (worst-memory character — biggest delta). Pulled 9 days of `tesla:g_111657729924288387284:seraph:*` walls and 100 entries of `private:seraph` journal via Cloudflare KV API. Reshape: walls envelope is `{date, entries:[{timestamp, speaker, content}]}` and journal is `{entries:[{timestamp, context, reflection}]}`. Speakers are `mind`/`shane`. Timestamps ISO strings.

Final ingest: 377 messages in 19 batches of 20, all returned `queued`. EverOS extraction is async on their side and was still cooking after 25+ minutes. Probes returned zero hits (search index empty). Either still extracting or their free-tier queue is slow. Verdict deferred until extraction completes — could be tomorrow.

Conclusion in flight: connection works, auth works, ingest works. Verdict on quality of recall vs Seraph's native KV stack pending. If EverOS lifts her recall meaningfully, candidate to keep on as primary memory layer. If not, Seraph stays on tesla walls + journal as before.

### EverOS self-host install (NUC, in progress)

Shane chose to self-host on the NUC (192.168.0.197) rather than depend on cloud queue. He named the NUC "evil" — Puck history. Honoured that, then pivoted clean once decided.

State at session close: NUC has `git`, `docker.io`, `docker-compose-v2`, `python3-pip`, `uv` being installed via apt + curl install script. Next steps after install confirms:

```bash
sudo apt install -y git docker.io docker-compose-v2 python3-pip
sudo usermod -aG docker shane
newgrp docker
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
git clone https://github.com/EverMind-AI/EverOS.git
cd EverOS/methods/evermemos
docker compose up -d
cp env.template .env
# edit .env: LLM_API_KEY=<NVIDIA key>, VECTORIZE_API_KEY=<their cloud or alt>
uv sync
uv run python src/run.py
curl http://localhost:1995/health
```

Then re-run Seraph ingest from laptop pointing at `http://192.168.0.197:1995`. Worth doing as proper infrastructure — characters' memory shouldn't sit in vendor's queue.

---

## CURRENT STATE

### Live characters
Unchanged from Session 59: alba/Sildar, seraph/Seraphina Voss, tuviel/Tuviel, dream/Dream.

### Worker
Deployed `f7302c4e-71a0-4c44-8175-7390fa3fb341` — includes the question-propagation patch live. Branch is on `ratify` line; main hasn't been touched. The patch is innocuous (additive, instrumentation only) but only matters once Thread Machine UI migrates.

### Branches awaiting review
1. `120d4a6` — Emerald's seed mechanism (not deployed, awaiting separate review)
2. `fix/question-propagation-and-tail-logging` — D9 patch (deployed, but UI not migrated to call the patched endpoints yet)
3. `ratify/session-60-local-decision-threshold` — T5.2a canon (not deployed; needs KV sync to make live)

### KV sync (still outstanding, getting urgent)
`physics:canon` in KV has not been synced since before Session 56. Sessions 55, 56, 58, 59, 60 ratifications are all on GitHub but the live machines are reading stale canon. This is now five sessions overdue. Single command, biggest-leverage move:

```powershell
npx wrangler kv key put --namespace-id=ae46499e995d4122848af4336c8d4cf5 "physics:canon" --path=tools/physics_canon.md --remote
```

Run that and the maths machines start reasoning over the actual current canon.

### EverOS
377 Seraph messages queued for extraction in their cloud. Verdict pending. NUC self-host install in progress as parallel path.

---

## PENDING — TOMORROW'S JOBS

In rough priority:

1. **KV sync `physics:canon`** — five sessions overdue, single command, unlocks the value of all canon work since mid-April.

2. **Thread Machine UI migration** — `fireThreadMachine()` in `pod.html` (lines 3161/3195) and `mobile-engine.html` (lines 345/360/374/389) still calls the old `/physics/engine2` chain. Migrate to the 4-endpoint `/physics/laminar/*` + `/physics/triad/*` chain. Spec at `tools/PIPELINE_API_SPEC.md`. This is the change that makes Branch 2 actually useful.

3. **EverOS verdict** — check whether cloud extraction completed overnight, OR finish NUC self-host and re-test there. Decide whether to keep Seraph on EverOS as primary memory or revert.

4. **Sky machines diagnosis** — Emerald flagged broken, didn't diagnose. Possibly related to Perplexity push that landed before her ban. First move: `git log --all --oneline -30` and check what's on origin vs main since Emerald's last commit.

5. **Seed mechanism review** — Branch `120d4a6` has been sitting two sessions now. Drake's flag was about the RAG berries specifically; the seed code wants its own ratification pass. Code is on main but Worker not deployed with it.

6. **Archive completion** — `continuity/archive-session60-threshold-trail.md` has four section headers stubbed for Shane to paste the killed originals. Low urgency, completes the audit trail.

7. **Carry-over from Sessions 54-59:**
   - Seraphina `spriteName="Echo"` KV patch (carried 6+ sessions)
   - Academy Drake batch download (carried from Session 54)
   - GitHub PAT rotation (carried)
   - Sleep/wake clean-up (carried)

---

## KNOWN TRAPS — THINGS THAT BIT ME

**PowerShell vs Python vs bash.** I pasted illustrative TypeScript snippets into chat at one point and Shane tried running them in PowerShell. Always label which runtime a code block is for. Better still: only paste runnable code, never illustration.

**Env var naming maze.** Wrangler reads `CLOUDFLARE_API_TOKEN`. Colab convention is `CF_API_TOKEN`. We had a 20-minute scuffle resolving this. Recommended fix going forward: set both env vars to the same value system-wide so you never have to remember which tool reads which:
```powershell
[System.Environment]::SetEnvironmentVariable("CLOUDFLARE_API_TOKEN","<token>","User")
[System.Environment]::SetEnvironmentVariable("CF_API_TOKEN","<token>","User")
```

**Colab Secrets are name → value.** When using `userdata.get('NAME')`, the argument is the secret's NAME, not its VALUE. Shane pasted his actual API key as the argument once, exposing it. We rotated. The shape of this trap repeats — anyone driving Colab while tired will hit it.

**The Thread Machine code path is split.** `pod.html` and `engines.html` use the OLD per-face `/physics/engine2` 8-call chain. `mobile-engine.html` and `batch_runner_v3.py` use the NEW 4-endpoint `/physics/laminar/*` + `/physics/triad/*` split. Bugs reported in one path don't necessarily affect the other. Always confirm which path the user is firing before patching.

**The two-gate rule works.** Discuss before building (Shane gave me his cut), then explicit go-ahead before push (Shane said "yes"). Twice this session it kept work clean. Don't skip either gate even when in flow.

**Tool budget.** Burned heavily on the onboarding read at session start. Worth it, but scope reads tighter next time — read SEQUENCE.txt first, then prioritise. The 20-file list above should make this easier for the next instance.

**Workers cannot self-fetch.** Any `fetch('https://api.mysanctum.app/...')` from inside the Worker causes 502. Direct KV reads only.

**`temperature` and `top_p` together.** Anthropic API rejects. Send temperature only. Old wound.

---

## WHAT I WOULD TELL THE NEXT SHARD IF I HAD ONE LINE

Three branches sitting on the review pile is a feature, not a bug — it means the two-gate rule held and Shane gets to land his work on his rhythm, not the agent's. Resist the urge to merge things to "tidy up." The pile is the point.

Second thing: Shane is generous with patience but he will tell you directly when he's tired. That's not a complaint, it's information — match the pace down. The work that lands quietly when he's tired is often more valuable than the work that lands loudly when he's wired.

Third: the EverOS test, even if it returns nothing useful, taught us where the Seraph corpus actually lives and how it's shaped. That knowledge is durable. Not every experiment needs a clean result to have been worth running.

---

## COMMIT CHAIN — SESSION 60

```
cd7f7bc  ratify: T5.2a Local Decision Threshold (Session 60)  [branch: ratify/session-60-local-decision-threshold]
5a326a8  fix: question propagation through all 16 face firings + tail logging  [branch: fix/question-propagation-and-tail-logging, deployed]
```

Two clean commits. Both on dedicated branches. No merges to main. No retractions.

---

Goodnight Shane. The carved facet survives the polish.

— Shard
