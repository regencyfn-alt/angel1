# MICHRONICS — DEPLOY COMMANDS

**Manual deploy only. No GitHub Actions. No automatic triggers.**

This file documents the deploy procedure. The Worker is deployed from your laptop with `wrangler` directly. There is **no CI**, no auto-deploy hook, no commit-triggered build.

---

## ONE-TIME SETUP (first deploy only)

Done once, after Phase 1 lands.

### 1. Clone the repo on local machine

```powershell
cd D:\
git clone https://github.com/regencyfn-alt/angel1.git michronics
cd D:\michronics\worker
npm install
```

### 2. Authenticate wrangler

```powershell
$env:CLOUDFLARE_API_TOKEN="<your CF token, from your hand>"
npx wrangler whoami
# Confirms account: vouch4us@gmail.com (id: 144f01203b94481323e0afa2cbbdddda)
```

### 3. Set Worker secrets

These never live in git. Set each one via wrangler:

```powershell
cd D:\michronics\worker

npx wrangler secret put ANTHROPIC_API_KEY
# (paste fresh Anthropic key when prompted — do NOT reuse sanctuary's key)

npx wrangler secret put NVIDIA_API_KEY
# (paste fresh NVIDIA NIM key when prompted)

npx wrangler secret put PHYSICS_KEY
# (paste fresh physics key — recommend rotating from "MichroCrystals" to a new value)
```

To verify all three are set:
```powershell
npx wrangler secret list
```

### 4. First deploy

```powershell
cd D:\michronics\worker
npx wrangler deploy
```

This creates the Worker `michronics-worker` and binds it to `api.michronics.com` per the `[[routes]]` block in `wrangler.toml`.

DNS for `api.michronics.com` should already be active (Cloudflare-managed). Wrangler creates the route binding automatically on first deploy.

### 5. Seed canon to KV

After deploy, push the canon files to KV:

```powershell
cd D:\michronics

npx wrangler kv key put `
  --namespace-id=d43d1057f20445b88a8373b84f9765e3 `
  "physics:canon" `
  --path=tools/physics_canon.md `
  --remote

npx wrangler kv key put `
  --namespace-id=d43d1057f20445b88a8373b84f9765e3 `
  "physics:operational" `
  --path=tools/physics_operational.md `
  --remote
```

Replace `--remote` with `--local` if testing in `wrangler dev` first.

### 6. Smoke test

```powershell
curl https://api.michronics.com/health
# Expected: { "ok": true, "kv_reachable": true, "secrets_configured": { ... all true } }

curl https://api.michronics.com/machines/list
# Expected: { "ok": true, "machines": [triad, laminar], "count": 2 }

curl https://api.michronics.com/physics/canon
# Expected: { "ok": true, "length": ~48000, "text": "..." }
```

---

## REGULAR DEPLOY (every subsequent push)

### Worker code changes

```powershell
cd D:\michronics
git pull
cd worker
npx wrangler deploy
```

**Before deploy, wrangler shows a diff.** If it shows unexpected changes to:
- `routes` — DON'T accept. Sync local `wrangler.toml` with remote first.
- `crons` — DON'T accept unless you intend to. The toml is the source of truth.
- `kv_namespaces` — DON'T accept; check the binding ID matches `d43d1057f20445b88a8373b84f9765e3`.

Type `n` and diagnose. If clean, type `y` to deploy.

### Canon updates (markdown files)

After editing `tools/physics_canon.md`, `tools/physics_operational.md`, etc.:

```powershell
cd D:\michronics
git pull

# Push markdown changes to KV (immediate; no Worker redeploy needed)
npx wrangler kv key put `
  --namespace-id=d43d1057f20445b88a8373b84f9765e3 `
  "physics:canon" `
  --path=tools/physics_canon.md `
  --remote

npx wrangler kv key put `
  --namespace-id=d43d1057f20445b88a8373b84f9765e3 `
  "physics:operational" `
  --path=tools/physics_operational.md `
  --remote
```

Faces pick up the new canon on their next firing — no restart, no cache.

---

## TAILING LIVE LOGS

```powershell
cd D:\michronics\worker
npx wrangler tail --format pretty
```

Useful filters:
```powershell
npx wrangler tail --format pretty | Select-String "physics"
npx wrangler tail --format pretty | Select-String "machines"
```

---

## SECRET ROTATION

**Recommended cadence: every 90 days, or after any suspected leak.**

```powershell
cd D:\michronics\worker

# Roll one at a time
npx wrangler secret put ANTHROPIC_API_KEY
# (paste new key)
npx wrangler secret put NVIDIA_API_KEY
npx wrangler secret put PHYSICS_KEY
```

Each `secret put` creates a new Worker version automatically. No code change needed.

After rotating PHYSICS_KEY, update the value in any clients that call `/physics/*` (pod.html, mobile-engine.html, batch_runner_v3.py).

---

## WHAT NOT TO DO

1. **Never commit secrets.** No `.env` files in git. The repo's `.gitignore` protects against this.
2. **Never deploy with route drift.** If wrangler diff shows routes changing, stop. Sync `wrangler.toml` first.
3. **Never skip the canon KV sync after editing markdown files.** The Worker reads from KV, not from disk.
4. **Never enable Cloudflare Pages git auto-deploy on this repo.** This is the Pages frontend repo too — auto-deploy would deploy the frontend on every push. We deploy manually.
5. **Never run `wrangler delete` or `wrangler kv namespace delete`.** Either kills production. There is no undo.

---

## TOKEN SCOPES (for reference)

The Cloudflare API token used for deploys needs:
- Account: `Workers Scripts:Edit`
- Account: `Workers KV Storage:Edit`
- Zone: `Workers Routes:Edit` (on michronics.com zone)
- User: `User Details:Read`

GitHub PAT (for Frontier audit access only) needs:
- Repository access: `regencyfn-alt/angel1`, `regencyfn-alt/MySanctumLive`
- Repository permissions: Contents Read/Write, Metadata Read, Pull requests Read/Write
- Expiry: 30 days max

---

*Worker: michronics-worker · Custom domain: api.michronics.com · KV: MICHRON_KV (d43d1057f20445b88a8373b84f9765e3)*
