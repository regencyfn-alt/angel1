// Michronics Worker — Environment Bindings
// Lean: only what the maths actually needs.
//
// Secrets set via `wrangler secret put` from local laptop:
//   ANTHROPIC_API_KEY  — D9 synthesis on Opus
//   NVIDIA_API_KEY     — Llama 70B / Nemotron faces
//   PHYSICS_KEY        — auth header X-Physics-Key for /physics/* endpoints

export interface Env {
  // KV — Michronics namespace only. Sanctuary keeps its own.
  MICHRON_KV: KVNamespace;

  // Workers AI binding — used for Llama 3.1 70B face firings via env.AI.run()
  AI: any;

  // Secrets
  ANTHROPIC_API_KEY: string;
  NVIDIA_API_KEY: string;
  PHYSICS_KEY: string;

  // Optional — only if batch runner uses Worker as canon proxy
  GITHUB_PAT?: string;

  // Var
  ENVIRONMENT: string;
}
